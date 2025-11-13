#!/usr/bin/env python3
"""
PDB Structure Downloader for Ketamine Docking Pipeline
Downloads protein structures for NMDA, EGFR, and CSNK1D targets
"""

import os
import sys
from pathlib import Path
from Bio.PDB import PDBList
import urllib.request
import time

# Define project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "proteins"

# Target structures
TARGETS = {
    "NMDA": {
        "priority": 1,
        "description": "NMDA Receptor GluN2B subunit - Primary ketamine target",
        "structures": {
            "7EU8": "GluN1-GluN2B + S-ketamine complex (human)",
            "4PE5": "GluN1a/GluN2B NMDA receptor",
            "5IPR": "GluN1/GluN2B NMDA receptor"
        }
    },
    "EGFR": {
        "priority": 2,
        "description": "EGFR kinase domain - EGF expression significantly reduced",
        "structures": {
            "4I24": "EGFR kinase domain (wild-type)",
            "4G5J": "EGFR kinase + inhibitor complex",
            "2GS6": "Active EGFR kinase domain"
        }
    },
    "CSNK1D": {
        "priority": 3,
        "description": "Casein Kinase 1 Delta - Wnt/β-catenin pathway",
        "structures": {
            "6GZM": "CSNK1D with inhibitor",
            "5OKS": "CSNK1D catalytic domain"
        }
    }
}


def download_pdb_structure(pdb_id, output_dir):
    """
    Download PDB structure using BioPython PDBList

    Args:
        pdb_id: 4-character PDB ID
        output_dir: Directory to save PDB file

    Returns:
        Path to downloaded file or None if failed
    """
    pdb_list = PDBList()

    try:
        print(f"  Downloading {pdb_id}...", end=" ")

        # Download to temporary location
        pdb_file = pdb_list.retrieve_pdb_file(
            pdb_id,
            pdir=str(output_dir),
            file_format='pdb'
        )

        # Rename to standard format
        standard_name = output_dir / f"{pdb_id.lower()}.pdb"

        # PDBList downloads as pdbXXXX.ent, rename it
        downloaded_file = Path(pdb_file)
        if downloaded_file.exists():
            downloaded_file.rename(standard_name)
            print(f"✓ Saved to {standard_name.name}")
            return standard_name
        else:
            print("✗ Failed")
            return None

    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def download_all_structures():
    """Download all target structures"""

    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - PDB Structure Downloader")
    print("=" * 70)
    print()

    # Create output directory
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    total_structures = 0
    downloaded = 0
    failed = []

    # Download for each target
    for target_name, target_info in sorted(TARGETS.items(), key=lambda x: x[1]['priority']):
        print(f"\n{'='*70}")
        print(f"TARGET: {target_name} (Priority {target_info['priority']})")
        print(f"Description: {target_info['description']}")
        print(f"{'='*70}")

        target_dir = DATA_DIR / target_name.lower()
        target_dir.mkdir(exist_ok=True)

        structures = target_info['structures']
        print(f"Structures to download: {len(structures)}\n")

        for pdb_id, description in structures.items():
            total_structures += 1
            print(f"[{pdb_id}] {description}")

            result = download_pdb_structure(pdb_id, target_dir)

            if result:
                downloaded += 1
            else:
                failed.append(f"{target_name}/{pdb_id}")

            # Be nice to PDB servers
            time.sleep(1)

    # Summary
    print(f"\n{'='*70}")
    print("DOWNLOAD SUMMARY")
    print(f"{'='*70}")
    print(f"Total structures: {total_structures}")
    print(f"Successfully downloaded: {downloaded}")
    print(f"Failed: {len(failed)}")

    if failed:
        print(f"\nFailed downloads:")
        for item in failed:
            print(f"  - {item}")

    print(f"\nAll structures saved to: {DATA_DIR}")
    print("=" * 70)

    return downloaded, len(failed)


def main():
    """Main execution"""
    try:
        success, failures = download_all_structures()

        if failures > 0:
            sys.exit(1)
        else:
            print("\n✓ All structures downloaded successfully!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
