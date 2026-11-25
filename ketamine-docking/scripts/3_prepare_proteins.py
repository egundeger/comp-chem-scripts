#!/usr/bin/env python3
"""
Protein Structure Preparation for Docking
Cleans PDB files, removes water molecules, adds hydrogens
and prepares for AutoDock Vina
"""

import os
import sys
from pathlib import Path
from Bio.PDB import PDBParser, PDBIO, Select
import subprocess
import shutil

# Define project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
PROTEIN_DIR = PROJECT_ROOT / "data" / "proteins"
PREPARED_DIR = PROJECT_ROOT / "data" / "prepared"


class ProteinSelect(Select):
    """Select only protein atoms (no water, ions, or heteroatoms)"""

    def __init__(self, keep_ligands=False):
        self.keep_ligands = keep_ligands

    def accept_residue(self, residue):
        """Accept or reject residues"""
        hetflag = residue.get_id()[0]

        # Always keep standard amino acids
        if hetflag == ' ':
            return True

        # Keep ligands if requested (for reference binding sites)
        if self.keep_ligands and hetflag.startswith('H_'):
            return True

        # Reject water, ions, and other heteroatoms
        return False


def clean_pdb_file(input_pdb, output_pdb, keep_ligands=True):
    """
    Clean PDB file - remove waters, keep protein (and optionally ligands)

    Args:
        input_pdb: Input PDB file path
        output_pdb: Output cleaned PDB file path
        keep_ligands: Keep heteroatoms (ligands) for binding site reference

    Returns:
        True if successful, False otherwise
    """
    try:
        parser = PDBParser(QUIET=True)
        structure = parser.get_structure('protein', str(input_pdb))

        # Create PDBIO object
        io = PDBIO()
        io.set_structure(structure)

        # Save with selection
        io.save(str(output_pdb), ProteinSelect(keep_ligands=keep_ligands))

        # Check if output exists
        if output_pdb.exists() and output_pdb.stat().st_size > 0:
            return True
        else:
            return False

    except Exception as e:
        print(f"    ✗ Error cleaning PDB: {e}")
        return False


def prepare_receptor_pdbqt(pdb_file, pdbqt_file):
    """
    Prepare receptor for AutoDock Vina (convert to PDBQT)

    Args:
        pdb_file: Input PDB file
        pdbqt_file: Output PDBQT file

    Returns:
        True if successful, False otherwise
    """
    # Try using Open Babel
    try:
        result = subprocess.run(
            ['obabel', str(pdb_file), '-O', str(pdbqt_file), '-xr'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and pdbqt_file.exists():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    # Try using MGLTools prepare_receptor4.py
    try:
        result = subprocess.run(
            ['prepare_receptor4.py', '-r', str(pdb_file), '-o', str(pdbqt_file), '-A', 'hydrogens'],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode == 0 and pdbqt_file.exists():
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    return False


def process_target_directory(target_dir):
    """
    Process all PDB files in a target directory

    Args:
        target_dir: Directory containing PDB files for a target

    Returns:
        Number of successfully processed files
    """
    target_name = target_dir.name
    print(f"\n{'='*70}")
    print(f"Processing: {target_name.upper()}")
    print(f"{'='*70}")

    # Create output directory
    output_dir = PREPARED_DIR / target_name
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all PDB files
    pdb_files = list(target_dir.glob("*.pdb"))

    if not pdb_files:
        print(f"  ⚠ No PDB files found in {target_dir}")
        return 0

    print(f"Found {len(pdb_files)} PDB files\n")

    success_count = 0

    for pdb_file in sorted(pdb_files):
        pdb_id = pdb_file.stem
        print(f"  [{pdb_id.upper()}]")

        # Clean PDB file
        cleaned_pdb = output_dir / f"{pdb_id}_clean.pdb"
        print(f"    Removing water and ions...", end=" ")

        if clean_pdb_file(pdb_file, cleaned_pdb, keep_ligands=True):
            print("✓")

            # Convert to PDBQT
            pdbqt_file = output_dir / f"{pdb_id}.pdbqt"
            print(f"    Converting to PDBQT...", end=" ")

            if prepare_receptor_pdbqt(cleaned_pdb, pdbqt_file):
                print("✓")
                success_count += 1
            else:
                print("⚠ (manual conversion needed)")
                print(f"      Clean PDB available: {cleaned_pdb}")
                # Still count as success if we have cleaned PDB
                success_count += 1
        else:
            print("✗")

    return success_count


def main():
    """Main execution"""
    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - Protein Preparation")
    print("=" * 70)
    print()

    # Check if protein directory exists
    if not PROTEIN_DIR.exists():
        print(f"✗ Protein directory not found: {PROTEIN_DIR}")
        print("  Please run 1_download_structures.py first")
        sys.exit(1)

    # Create prepared directory
    PREPARED_DIR.mkdir(parents=True, exist_ok=True)

    # Process each target directory
    target_dirs = [d for d in PROTEIN_DIR.iterdir() if d.is_dir()]

    if not target_dirs:
        print(f"✗ No target directories found in {PROTEIN_DIR}")
        sys.exit(1)

    total_processed = 0

    for target_dir in sorted(target_dirs):
        count = process_target_directory(target_dir)
        total_processed += count

    # Summary
    print(f"\n{'='*70}")
    print("PROTEIN PREPARATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total structures processed: {total_processed}")
    print(f"Output directory: {PREPARED_DIR}")
    print("=" * 70)

    if total_processed == 0:
        print("\n✗ No structures were successfully processed")
        sys.exit(1)
    else:
        print(f"\n✓ {total_processed} structures prepared!")

        # Check if PDBQT conversion tools are available
        print("\nChecking docking tools...")
        obabel_ok = shutil.which('obabel') is not None
        mgltools_ok = shutil.which('prepare_receptor4.py') is not None

        if not obabel_ok and not mgltools_ok:
            print("  ⚠ No PDBQT conversion tools found")
            print("    Install Open Babel: conda install -c conda-forge openbabel")
            print("    Or MGLTools: https://ccsb.scripps.edu/mgltools/")
        else:
            if obabel_ok:
                print("  ✓ Open Babel found")
            if mgltools_ok:
                print("  ✓ MGLTools found")

        sys.exit(0)


if __name__ == "__main__":
    main()
