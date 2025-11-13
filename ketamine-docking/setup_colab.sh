#!/bin/bash
# Google Colab Setup Script for Ketamine Docking Pipeline
# Run this in Colab to install all dependencies

set -e  # Exit on error

echo "=========================================================================="
echo "Ketamine Docking Pipeline - Google Colab Setup"
echo "=========================================================================="
echo ""

# Update system
echo "📦 Updating system packages..."
apt-get update -qq > /dev/null 2>&1

# Install Python packages
echo "🐍 Installing Python packages..."
pip install -q biopython rdkit pandas pyyaml openpyxl matplotlib seaborn scipy numpy

# Install Open Babel
echo "🧪 Installing Open Babel..."
apt-get install -qq -y openbabel > /dev/null 2>&1

# Install AutoDock Vina
echo "🔬 Installing AutoDock Vina..."
if [ ! -f "/usr/local/bin/vina" ]; then
    wget -q https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O /tmp/vina
    chmod +x /tmp/vina
    mv /tmp/vina /usr/local/bin/vina
    echo "  ✓ Vina installed"
else
    echo "  ✓ Vina already installed"
fi

# Verify installations
echo ""
echo "=========================================================================="
echo "Verifying installations..."
echo "=========================================================================="

# Python version
python --version

# Python packages
python -c "import Bio; print('✓ BioPython')" || echo "✗ BioPython FAILED"
python -c "import rdkit; print('✓ RDKit')" || echo "✗ RDKit FAILED"
python -c "import pandas; print('✓ Pandas')" || echo "✗ Pandas FAILED"
python -c "import yaml; print('✓ PyYAML')" || echo "✗ PyYAML FAILED"

# External tools
which vina > /dev/null && vina --version | head -1 || echo "✗ Vina FAILED"
which obabel > /dev/null && echo "✓ Open Babel" || echo "✗ Open Babel FAILED"

echo ""
echo "=========================================================================="
echo "✓ Setup complete!"
echo "=========================================================================="
echo ""
echo "Next steps:"
echo "  1. Clone repository: git clone https://github.com/egundeger/comp-chem-scripts.git"
echo "  2. cd comp-chem-scripts/ketamine-docking"
echo "  3. python run_pipeline.py --all"
echo ""
