#!/usr/bin/env python3
"""
AutoDock Vina Docking Script
Performs molecular docking for ketamine against protein targets
"""

import os
import sys
import yaml
import subprocess
from pathlib import Path
from datetime import datetime
import json

# Define project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
CONFIG_DIR = PROJECT_ROOT / "configs"
PREPARED_DIR = PROJECT_ROOT / "data" / "prepared"
LIGAND_DIR = PROJECT_ROOT / "data" / "ligands"
RESULTS_DIR = PROJECT_ROOT / "data" / "results"


def load_config(config_file):
    """Load target configuration from YAML file"""
    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"  ✗ Error loading config: {e}")
        return None


def find_ligand_center(pdb_file):
    """
    Find center of mass of a ligand in PDB file
    Used for auto-detecting binding site from co-crystallized ligands

    Args:
        pdb_file: PDB file containing ligand

    Returns:
        (x, y, z) coordinates or None
    """
    try:
        from Bio.PDB import PDBParser

        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', str(pdb_file))

        coords = []
        for model in structure:
            for chain in model:
                for residue in chain:
                    hetflag = residue.get_id()[0]
                    # Look for heteroatoms (ligands)
                    if hetflag.startswith('H_'):
                        for atom in residue:
                            coords.append(atom.get_coord())

        if coords:
            import numpy as np
            center = np.mean(coords, axis=0)
            return tuple(center)
        else:
            return None

    except Exception as e:
        print(f"    ⚠ Could not auto-detect binding site: {e}")
        return None


def create_vina_config(receptor_file, ligand_file, config_data, output_dir):
    """
    Create AutoDock Vina configuration file

    Args:
        receptor_file: Path to receptor PDBQT file
        ligand_file: Path to ligand PDBQT file
        config_data: Dictionary with docking parameters
        output_dir: Output directory for results

    Returns:
        Path to config file or None
    """
    try:
        config_file = output_dir / "vina_config.txt"

        # Get binding site coordinates
        binding_site = config_data.get('binding_site', {})

        center_x = binding_site.get('center_x', 0.0)
        center_y = binding_site.get('center_y', 0.0)
        center_z = binding_site.get('center_z', 0.0)
        size_x = binding_site.get('size_x', 25.0)
        size_y = binding_site.get('size_y', 25.0)
        size_z = binding_site.get('size_z', 25.0)

        # Auto-detect binding site if requested
        if binding_site.get('auto_detect', False):
            center = find_ligand_center(receptor_file)
            if center:
                center_x, center_y, center_z = center
                print(f"    Auto-detected binding site: ({center_x:.2f}, {center_y:.2f}, {center_z:.2f})")
        elif 'manual_center' in binding_site:
            manual = binding_site['manual_center']
            center_x = manual.get('x', center_x)
            center_y = manual.get('y', center_y)
            center_z = manual.get('z', center_z)

        exhaustiveness = config_data.get('exhaustiveness', 20)
        num_modes = config_data.get('num_modes', 10)

        # Write configuration
        with open(config_file, 'w') as f:
            f.write(f"receptor = {receptor_file}\n")
            f.write(f"ligand = {ligand_file}\n")
            f.write(f"\n")
            f.write(f"center_x = {center_x}\n")
            f.write(f"center_y = {center_y}\n")
            f.write(f"center_z = {center_z}\n")
            f.write(f"\n")
            f.write(f"size_x = {size_x}\n")
            f.write(f"size_y = {size_y}\n")
            f.write(f"size_z = {size_z}\n")
            f.write(f"\n")
            f.write(f"exhaustiveness = {exhaustiveness}\n")
            f.write(f"num_modes = {num_modes}\n")

        return config_file

    except Exception as e:
        print(f"    ✗ Error creating Vina config: {e}")
        return None


def run_vina(config_file, output_file, log_file):
    """
    Run AutoDock Vina docking

    Args:
        config_file: Vina configuration file
        output_file: Output PDBQT file for results
        log_file: Log file for Vina output

    Returns:
        True if successful, False otherwise
    """
    try:
        # Note: Vina 1.2.x doesn't support --log parameter
        # We capture output and write it manually
        cmd = [
            'vina',
            '--config', str(config_file),
            '--out', str(output_file)
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )

        # Write log file manually
        with open(log_file, 'w') as f:
            f.write("AutoDock Vina Output\n")
            f.write("=" * 70 + "\n\n")
            if result.stdout:
                f.write(result.stdout)
            if result.stderr:
                f.write("\n\nStderr:\n")
                f.write(result.stderr)

        if result.returncode == 0:
            return True
        else:
            print(f"    ✗ Vina failed with return code {result.returncode}")
            if result.stderr:
                print(f"    Error: {result.stderr[:200]}")  # Show first 200 chars
            return False

    except FileNotFoundError:
        print(f"    ✗ AutoDock Vina not found in PATH")
        print(f"      Install: conda install -c conda-forge vina")
        return False
    except subprocess.TimeoutExpired:
        print(f"    ✗ Vina timed out (>1 hour)")
        return False
    except Exception as e:
        print(f"    ✗ Error running Vina: {e}")
        return False


def parse_vina_output(log_file):
    """
    Parse AutoDock Vina output log file to extract binding energies

    Args:
        log_file: Path to Vina log file

    Returns:
        List of (mode, affinity, rmsd_lb, rmsd_ub) tuples
    """
    results = []

    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()

        parsing = False
        for line in lines:
            if '-----+' in line and 'mode' in lines[lines.index(line) - 1]:
                parsing = True
                continue

            if parsing and line.strip() and not line.startswith('---'):
                parts = line.split()
                if len(parts) >= 4 and parts[0].isdigit():
                    mode = int(parts[0])
                    affinity = float(parts[1])
                    rmsd_lb = float(parts[2])
                    rmsd_ub = float(parts[3])
                    results.append((mode, affinity, rmsd_lb, rmsd_ub))

    except Exception as e:
        print(f"    ⚠ Error parsing Vina output: {e}")

    return results


def perform_docking(target_name, config_file):
    """
    Perform docking for a target

    Args:
        target_name: Name of target (nmda, egfr, csnk1d)
        config_file: Path to configuration file

    Returns:
        Dictionary of results
    """
    print(f"\n{'='*70}")
    print(f"TARGET: {target_name.upper()}")
    print(f"{'='*70}")

    # Load configuration
    config = load_config(config_file)
    if not config:
        return None

    print(f"Description: {config.get('description', 'N/A')}")
    print(f"Priority: {config.get('priority', 'N/A')}")

    # Prepare output directory
    target_results_dir = RESULTS_DIR / target_name
    target_results_dir.mkdir(parents=True, exist_ok=True)

    # Get structures
    structures = config.get('structures', {})
    print(f"\nStructures to dock: {len(structures)}")

    all_results = {}

    # Process each structure
    for pdb_id, structure_config in structures.items():
        print(f"\n  [{pdb_id.upper()}] {structure_config.get('description', '')}")

        # Find receptor file
        receptor_dir = PREPARED_DIR / target_name
        receptor_pdbqt = receptor_dir / f"{pdb_id.lower()}.pdbqt"

        if not receptor_pdbqt.exists():
            print(f"    ✗ Receptor PDBQT not found: {receptor_pdbqt}")
            continue

        # Process each ligand form
        ligand_forms = ['S-ketamine', 'R-ketamine', 'racemic-ketamine']

        for ligand_name in ligand_forms:
            ligand_pdbqt = LIGAND_DIR / f"{ligand_name}.pdbqt"

            if not ligand_pdbqt.exists():
                print(f"    ⚠ Ligand PDBQT not found: {ligand_pdbqt.name}")
                continue

            print(f"\n    Docking {ligand_name}...")

            # Create output directory
            output_dir = target_results_dir / pdb_id / ligand_name
            output_dir.mkdir(parents=True, exist_ok=True)

            # Create Vina config
            vina_config = create_vina_config(
                receptor_pdbqt,
                ligand_pdbqt,
                structure_config,
                output_dir
            )

            if not vina_config:
                continue

            # Output files
            output_pdbqt = output_dir / "docked_poses.pdbqt"
            log_file = output_dir / "vina.log"

            print(f"    Running AutoDock Vina...")

            # Run docking
            if run_vina(vina_config, output_pdbqt, log_file):
                print(f"    ✓ Docking completed")

                # Parse results
                results = parse_vina_output(log_file)

                if results:
                    best_affinity = results[0][1]
                    print(f"    Best binding affinity: {best_affinity:.2f} kcal/mol")

                    # Save results
                    result_key = f"{pdb_id}_{ligand_name}"
                    all_results[result_key] = {
                        'pdb_id': pdb_id,
                        'ligand': ligand_name,
                        'best_affinity': best_affinity,
                        'all_modes': results,
                        'output_dir': str(output_dir)
                    }
                else:
                    print(f"    ⚠ Could not parse docking results")
            else:
                print(f"    ✗ Docking failed")

    return all_results


def main():
    """Main execution"""
    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - AutoDock Vina Docking")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Check required directories
    if not PREPARED_DIR.exists():
        print("✗ Prepared structures not found")
        print("  Please run 3_prepare_proteins.py first")
        sys.exit(1)

    if not LIGAND_DIR.exists():
        print("✗ Ligand structures not found")
        print("  Please run 2_prepare_ligand.py first")
        sys.exit(1)

    # Create results directory
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Load all configs
    targets = [
        ('nmda', CONFIG_DIR / 'nmda_targets.yaml'),
        ('egfr', CONFIG_DIR / 'egfr_targets.yaml'),
        ('csnk1d', CONFIG_DIR / 'csnk1d_targets.yaml')
    ]

    all_results = {}

    # Perform docking for each target
    for target_name, config_file in targets:
        if config_file.exists():
            results = perform_docking(target_name, config_file)
            if results:
                all_results[target_name] = results
        else:
            print(f"⚠ Config not found: {config_file}")

    # Save combined results
    results_json = RESULTS_DIR / "all_results.json"
    with open(results_json, 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*70}")
    print("DOCKING SUMMARY")
    print(f"{'='*70}")
    print(f"Results saved to: {RESULTS_DIR}")
    print(f"Summary file: {results_json}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == "__main__":
    main()
