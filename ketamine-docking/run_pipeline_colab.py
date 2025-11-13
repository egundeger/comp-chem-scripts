#!/usr/bin/env python3
"""
Ketamine Docking Pipeline - Google Colab Version
Non-interactive version for automated execution in Colab
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime


SCRIPT_DIR = Path(__file__).parent
SCRIPTS = SCRIPT_DIR / "scripts"


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(text)
    print("=" * 70 + "\n")


def run_script(script_path, description):
    """
    Run a Python script and handle errors

    Args:
        script_path: Path to Python script
        description: Description of the step

    Returns:
        True if successful, False otherwise
    """
    print_header(f"STEP: {description}")
    print(f"Running: {script_path.name}")
    print(f"Started: {datetime.now().strftime('%H:%M:%S')}\n")

    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=False
        )

        if result.returncode == 0:
            print(f"\n✓ {description} completed successfully")
            return True
        else:
            print(f"\n✗ {description} failed with return code {result.returncode}")
            return False

    except Exception as e:
        print(f"\n✗ Error running {description}: {e}")
        return False


def main():
    """Main pipeline execution - non-interactive for Colab"""

    # Pipeline configuration
    pipeline_steps = [
        (SCRIPTS / '1_download_structures.py', 'Download PDB Structures'),
        (SCRIPTS / '2_prepare_ligand.py', 'Prepare Ketamine Ligand'),
        (SCRIPTS / '3_prepare_proteins.py', 'Prepare Protein Structures'),
        (SCRIPTS / '4_run_docking.py', 'Run AutoDock Vina Docking'),
        (SCRIPTS / '5_analyze_results.py', 'Analyze Results and Generate Reports')
    ]

    # Print pipeline info
    print_header("KETAMINE DOCKING PIPELINE - GOOGLE COLAB")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {SCRIPT_DIR}")
    print("\nSteps to run:")
    for script_path, description in pipeline_steps:
        print(f"  ✓ {description}")

    print("\n🚀 Starting pipeline automatically (Colab mode - no user input required)")
    print("⏱️  Estimated time: 1-2 hours for complete analysis")
    print()

    # Execute pipeline
    failed_steps = []
    completed_steps = []

    start_time = datetime.now()

    for script_path, description in pipeline_steps:
        if not script_path.exists():
            print(f"\n✗ Script not found: {script_path}")
            failed_steps.append(description)
            break

        success = run_script(script_path, description)

        if success:
            completed_steps.append(description)
        else:
            failed_steps.append(description)
            print(f"\n✗ Pipeline stopped due to failure in: {description}")
            break

    # Final summary
    end_time = datetime.now()
    duration = end_time - start_time

    print_header("PIPELINE SUMMARY")
    print(f"Started:  {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration}")
    print()
    print(f"Completed steps: {len(completed_steps)}")
    for step in completed_steps:
        print(f"  ✓ {step}")

    if failed_steps:
        print()
        print(f"Failed steps: {len(failed_steps)}")
        for step in failed_steps:
            print(f"  ✗ {step}")
        print()
        print("=" * 70)
        print("PIPELINE FAILED")
        print("=" * 70)
        sys.exit(1)
    else:
        print()
        print("=" * 70)
        print("PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print()
        print("Next steps:")
        print("  1. Review results in data/results/reports/")
        print("  2. Download results ZIP file to your computer")
        print("  3. Run download cell in Colab notebook")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
