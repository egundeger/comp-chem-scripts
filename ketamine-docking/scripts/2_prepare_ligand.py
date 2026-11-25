#!/usr/bin/env python3
"""
Ketamine Ligand Preparation
Generates 3D structure of ketamine (S-ketamine and R-ketamine)
and converts to formats suitable for docking
"""

import os
import sys
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors
import subprocess

# Define project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
LIGAND_DIR = PROJECT_ROOT / "data" / "ligands"

# Ketamine SMILES
# S-Ketamine (Esketamine): The more potent enantiomer
KETAMINE_STRUCTURES = {
    "S-ketamine": {
        "smiles": "C[C@@H]1[C@@H](C(=O)c2ccccc2Cl)CCCCN1C",
        "description": "S-enantiomer (Esketamine) - More potent NMDA antagonist"
    },
    "R-ketamine": {
        "smiles": "C[C@H]1[C@H](C(=O)c2ccccc2Cl)CCCCN1C",
        "description": "R-enantiomer - Less potent but still active"
    },
    "racemic-ketamine": {
        "smiles": "CC1C(C(=O)c2ccccc2Cl)CCCCN1C",
        "description": "Racemic mixture (no stereochemistry)"
    }
}


def generate_3d_structure(smiles, output_file, name="ligand"):
    """
    Generate 3D structure from SMILES and save as PDB

    Args:
        smiles: SMILES string
        output_file: Output PDB file path
        name: Molecule name

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create molecule from SMILES
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            print(f"  ✗ Failed to parse SMILES: {smiles}")
            return False

        # Add hydrogens
        mol = Chem.AddHs(mol)

        # Generate 3D coordinates
        result = AllChem.EmbedMolecule(mol, randomSeed=42)
        if result != 0:
            print(f"  ✗ Failed to generate 3D coordinates")
            return False

        # Optimize geometry with MMFF force field
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)

        # Calculate properties
        mw = Descriptors.MolWt(mol)
        logp = Descriptors.MolLogP(mol)
        hbd = Descriptors.NumHDonors(mol)
        hba = Descriptors.NumHAcceptors(mol)

        print(f"  Molecular properties:")
        print(f"    MW: {mw:.2f} g/mol")
        print(f"    LogP: {logp:.2f}")
        print(f"    H-bond donors: {hbd}")
        print(f"    H-bond acceptors: {hba}")

        # Save as PDB
        Chem.MolToPDBFile(mol, str(output_file))
        print(f"  ✓ 3D structure saved to {output_file.name}")

        # Also save as MOL2 for some docking programs
        mol2_file = output_file.with_suffix('.mol2')
        Chem.MolToMolFile(mol, str(mol2_file))

        # Save as SDF
        sdf_file = output_file.with_suffix('.sdf')
        writer = Chem.SDWriter(str(sdf_file))
        writer.write(mol)
        writer.close()
        print(f"  ✓ Also saved as MOL2 and SDF formats")

        return True

    except Exception as e:
        print(f"  ✗ Error generating structure: {e}")
        return False


def prepare_for_autodock(pdb_file):
    """
    Prepare ligand for AutoDock Vina (convert to PDBQT)
    Requires Open Babel or MGLTools

    Args:
        pdb_file: Input PDB file

    Returns:
        Path to PDBQT file or None
    """
    pdbqt_file = pdb_file.with_suffix('.pdbqt')

    # Try using Open Babel first
    try:
        result = subprocess.run(
            ['obabel', str(pdb_file), '-O', str(pdbqt_file), '-p', '7.4'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and pdbqt_file.exists():
            print(f"  ✓ PDBQT file created: {pdbqt_file.name}")
            return pdbqt_file
        else:
            print(f"  ⚠ Open Babel conversion failed")
    except FileNotFoundError:
        print(f"  ⚠ Open Babel not found")
    except Exception as e:
        print(f"  ⚠ Error with Open Babel: {e}")

    # Try using MGLTools prepare_ligand4.py
    try:
        result = subprocess.run(
            ['prepare_ligand4.py', '-l', str(pdb_file), '-o', str(pdbqt_file), '-A', 'hydrogens'],
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode == 0 and pdbqt_file.exists():
            print(f"  ✓ PDBQT file created: {pdbqt_file.name}")
            return pdbqt_file
        else:
            print(f"  ⚠ MGLTools conversion failed")
    except FileNotFoundError:
        print(f"  ⚠ MGLTools not found")
    except Exception as e:
        print(f"  ⚠ Error with MGLTools: {e}")

    print(f"  ℹ Manual conversion to PDBQT required")
    print(f"    Install Open Babel: conda install -c conda-forge openbabel")
    print(f"    Or MGLTools: https://ccsb.scripps.edu/mgltools/")

    return None


def main():
    """Main execution"""
    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - Ligand Preparation")
    print("=" * 70)
    print()

    # Create output directory
    LIGAND_DIR.mkdir(parents=True, exist_ok=True)

    success_count = 0
    total_count = len(KETAMINE_STRUCTURES)

    # Generate structures for each form
    for name, info in KETAMINE_STRUCTURES.items():
        print(f"\n{'='*70}")
        print(f"Preparing: {name}")
        print(f"Description: {info['description']}")
        print(f"SMILES: {info['smiles']}")
        print(f"{'='*70}")

        output_file = LIGAND_DIR / f"{name}.pdb"

        # Generate 3D structure
        if generate_3d_structure(info['smiles'], output_file, name):
            success_count += 1

            # Try to convert to PDBQT
            prepare_for_autodock(output_file)
        else:
            print(f"  ✗ Failed to generate {name}")

    # Summary
    print(f"\n{'='*70}")
    print("LIGAND PREPARATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total ligands: {total_count}")
    print(f"Successfully prepared: {success_count}")
    print(f"Output directory: {LIGAND_DIR}")
    print("=" * 70)

    if success_count < total_count:
        print("\n⚠ Some ligands failed to generate")
        sys.exit(1)
    else:
        print("\n✓ All ligands prepared successfully!")
        sys.exit(0)


if __name__ == "__main__":
    main()
