#!/usr/bin/env python3
"""
Ketamine Docking Pipeline - Master Script
Orchestrates the complete docking workflow from structure download to analysis
"""

import os
import sys
import subprocess
import argparse
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
    """Main pipeline execution"""

    parser = argparse.ArgumentParser(
        description='Ketamine Docking Pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete pipeline
  python run_pipeline.py --all

  # Run specific steps
  python run_pipeline.py --download --prepare-ligand
  python run_pipeline.py --dock --analyze

  # Run from a specific step onwards
  python run_pipeline.py --from-dock

Steps:
  1. Download PDB structures (NMDA, EGFR, CSNK1D)
  2. Prepare ligand (Ketamine 3D structure)
  3. Prepare proteins (Clean PDB, convert to PDBQT)
  4. Run docking (AutoDock Vina)
  5. Analyze results (Generate reports)
        """
    )

    # Step selection arguments
    parser.add_argument('--all', action='store_true',
                        help='Run all steps')
    parser.add_argument('--download', action='store_true',
                        help='Download PDB structures')
    parser.add_argument('--prepare-ligand', action='store_true',
                        help='Prepare ketamine ligand')
    parser.add_argument('--prepare-proteins', action='store_true',
                        help='Prepare protein structures')
    parser.add_argument('--dock', action='store_true',
                        help='Run docking calculations')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyze docking results')

    # Convenience arguments
    parser.add_argument('--from-dock', action='store_true',
                        help='Run from docking step onwards')
    parser.add_argument('--skip-download', action='store_true',
                        help='Skip structure download (use existing)')

    args = parser.parse_args()

    # Determine which steps to run
    steps = {
        'download': args.all or args.download,
        'prepare_ligand': args.all or args.prepare_ligand,
        'prepare_proteins': args.all or args.prepare_proteins,
        'dock': args.all or args.dock or args.from_dock,
        'analyze': args.all or args.analyze or args.from_dock
    }

    # Handle skip-download
    if args.skip_download:
        steps['download'] = False

    # If no arguments, show help
    if not any(steps.values()):
        parser.print_help()
        sys.exit(0)

    # Pipeline configuration
    pipeline_steps = [
        ('download', SCRIPTS / '1_download_structures.py',
         'Download PDB Structures'),
        ('prepare_ligand', SCRIPTS / '2_prepare_ligand.py',
         'Prepare Ketamine Ligand'),
        ('prepare_proteins', SCRIPTS / '3_prepare_proteins.py',
         'Prepare Protein Structures'),
        ('dock', SCRIPTS / '4_run_docking.py',
         'Run AutoDock Vina Docking'),
        ('analyze', SCRIPTS / '5_analyze_results.py',
         'Analyze Results and Generate Reports')
    ]

    # Print pipeline info
    print_header("KETAMINE DOCKING PIPELINE")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Working directory: {SCRIPT_DIR}")
    print("\nSteps to run:")
    for step_name, script_path, description in pipeline_steps:
        if steps[step_name]:
            print(f"  ✓ {description}")
        else:
            print(f"  - {description} (skipped)")

    input("\nPress Enter to start pipeline (or Ctrl+C to cancel)...")

    # Execute pipeline
    failed_steps = []
    completed_steps = []

    start_time = datetime.now()

    for step_name, script_path, description in pipeline_steps:
        if not steps[step_name]:
            print(f"\n⊳ Skipping: {description}")
            continue

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
        print("  2. Visualize top-scoring poses with PyMOL or similar")
        print("  3. Validate findings with additional experiments")
        print("=" * 70)
        sys.exit(0)


if __name__ == "__main__":
    main()
