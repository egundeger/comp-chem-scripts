#!/usr/bin/env python3
"""
Dependency Checker for Ketamine Docking Pipeline
Verifies all required software and libraries are installed
"""

import sys
import subprocess
import importlib
from pathlib import Path


def check_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor} (need ≥3.8)")
        return False


def check_python_package(package_name, import_name=None):
    """Check if Python package is installed"""
    if import_name is None:
        import_name = package_name

    try:
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"  ✓ {package_name} ({version})")
        return True
    except ImportError:
        print(f"  ✗ {package_name} not found")
        print(f"      Install: pip install {package_name}")
        return False


def check_command(command, package_name=None):
    """Check if command-line tool is available"""
    if package_name is None:
        package_name = command

    try:
        result = subprocess.run(
            [command, '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            print(f"  ✓ {package_name}: {version}")
            return True
        else:
            print(f"  ⚠ {package_name} found but version check failed")
            return True  # Still count as available
    except FileNotFoundError:
        print(f"  ✗ {package_name} not found")
        return False
    except subprocess.TimeoutExpired:
        print(f"  ⚠ {package_name} timeout")
        return True  # Assume available
    except Exception as e:
        print(f"  ⚠ {package_name} check error: {e}")
        return False


def main():
    """Main dependency check"""
    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - Dependency Checker")
    print("=" * 70)
    print()

    all_ok = True

    # Core Python
    print("=" * 70)
    print("Core Requirements")
    print("=" * 70)
    all_ok &= check_python_version()
    print()

    # Python packages
    print("=" * 70)
    print("Python Packages")
    print("=" * 70)

    required_packages = [
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('scipy', 'scipy'),
        ('biopython', 'Bio'),
        ('rdkit', 'rdkit'),
        ('pyyaml', 'yaml'),
        ('matplotlib', 'matplotlib'),
        ('openpyxl', 'openpyxl'),
    ]

    for package_name, import_name in required_packages:
        all_ok &= check_python_package(package_name, import_name)

    print()

    # External tools
    print("=" * 70)
    print("External Tools")
    print("=" * 70)

    # Required
    print("\nRequired:")
    vina_ok = check_command('vina', 'AutoDock Vina')
    all_ok &= vina_ok

    if not vina_ok:
        print("      Install: conda install -c conda-forge vina")

    # Optional but recommended
    print("\nOptional (for PDBQT conversion):")
    obabel_ok = check_command('obabel', 'Open Babel')
    mgltools_ok = check_command('prepare_receptor4.py', 'MGLTools')

    if not obabel_ok and not mgltools_ok:
        print("  ⚠ No PDBQT conversion tools found")
        print("      Install Open Babel: conda install -c conda-forge openbabel")
        print("      Or MGLTools: https://ccsb.scripps.edu/mgltools/")
    elif obabel_ok:
        print("      (Open Babel found - sufficient)")
    elif mgltools_ok:
        print("      (MGLTools found - sufficient)")

    # Visualization tools (optional)
    print("\nOptional (for visualization):")
    check_command('pymol', 'PyMOL')
    print("      Install: conda install -c conda-forge pymol-open-source")

    # Summary
    print()
    print("=" * 70)
    print("Summary")
    print("=" * 70)

    if all_ok:
        print("✓ All required dependencies are installed!")
        print()
        print("You can now run the pipeline:")
        print("  python run_pipeline.py --all")
        print()
        return 0
    else:
        print("✗ Some required dependencies are missing")
        print()
        print("Install missing dependencies:")
        print()
        print("Python packages:")
        print("  pip install -r requirements.txt")
        print()
        print("AutoDock Vina:")
        print("  conda install -c conda-forge vina")
        print()
        print("Optional tools:")
        print("  conda install -c conda-forge openbabel pymol-open-source")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
