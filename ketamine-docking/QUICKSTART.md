# Ketamine Docking Pipeline - Quick Start Guide

## 🚀 Quick Start (5 Minutes)

### Step 1: Setup Environment

```bash
# Create conda environment
conda create -n ketamine-docking python=3.10 -y
conda activate ketamine-docking

# Install dependencies
cd ketamine-docking
pip install -r requirements.txt
conda install -c conda-forge vina openbabel -y
```

### Step 2: Run Pipeline

```bash
# Run complete pipeline (fully automated)
python run_pipeline.py --all
```

That's it! The pipeline will:
1. ⬇️ Download all PDB structures (NMDA, EGFR, CSNK1D)
2. 🧪 Generate 3D ketamine structures
3. 🔧 Prepare proteins for docking
4. 🎯 Perform molecular docking
5. 📊 Generate comprehensive reports

### Step 3: Check Results

```bash
# View results
cd data/results/reports/

# Summary files
cat overall_summary_*.txt
cat nmda_report_*.txt

# Excel report
open docking_results_*.xlsx  # or use Excel/LibreOffice
```

## ⚡ Common Use Cases

### Use Case 1: Quick Test Run
```bash
# Just download and prepare structures
python run_pipeline.py --download --prepare-ligand --prepare-proteins
```

### Use Case 2: Re-run Docking Only
```bash
# If structures already prepared
python run_pipeline.py --dock --analyze
```

### Use Case 3: Different Docking Parameters
```bash
# Edit configs first
nano configs/nmda_targets.yaml  # Change exhaustiveness, box size, etc.

# Then run docking
python run_pipeline.py --from-dock
```

## 📋 Expected Timeline

| Step | Time | Notes |
|------|------|-------|
| Download | 2-5 min | Depends on internet speed |
| Prepare Ligand | <1 min | Fast |
| Prepare Proteins | 1-2 min | Per target |
| Docking | 30-60 min | Per structure (depends on exhaustiveness) |
| Analysis | <1 min | Fast |
| **Total** | **1-2 hours** | For all targets |

## 🎯 Priority-Based Run

### Run Only NMDA (Highest Priority)
```bash
# 1. Download NMDA structures
python scripts/1_download_structures.py
# Edit script to only download NMDA if needed

# 2. Prepare
python scripts/2_prepare_ligand.py
python scripts/3_prepare_proteins.py

# 3. Dock NMDA only
# Edit scripts/4_run_docking.py: comment out EGFR and CSNK1D
python scripts/4_run_docking.py

# 4. Analyze
python scripts/5_analyze_results.py
```

### Run in Priority Order (Recommended)
```bash
# Run NMDA first (Priority 1)
# Then EGFR (Priority 2)
# Finally CSNK1D (Priority 3)

# This is done automatically with --all flag
python run_pipeline.py --all
```

## 🔍 Understanding Your Results

### Key Files to Check

1. **Overall Summary**
   ```
   data/results/reports/overall_summary_*.txt
   ```
   - Best binding affinity for each target
   - Target ranking
   - Key findings
   - Recommendations

2. **Individual Target Reports**
   ```
   data/results/reports/nmda_report_*.txt
   data/results/reports/egfr_report_*.txt
   data/results/reports/csnk1d_report_*.txt
   ```
   - Detailed results per structure
   - Binding mode analysis
   - Biological interpretation

3. **Excel Spreadsheet**
   ```
   data/results/reports/docking_results_*.xlsx
   ```
   - All docking modes
   - Sortable data
   - Easy comparison

### Interpreting Affinity Values

```
NMDA Receptor (Expected: -8 to -6 kcal/mol)
├─ Best: -7.5 kcal/mol → ✓ Strong binding (as expected)
└─ Interpretation: Confirms channel blocker mechanism

EGFR (Investigating EGF downregulation)
├─ Best: -5.2 kcal/mol → ⚠️ Weak binding
└─ Interpretation: EGF effects likely indirect

CSNK1D (Wnt pathway investigation)
├─ Best: -4.8 kcal/mol → ✗ No significant binding
└─ Interpretation: Downstream or upstream regulation
```

## 🎨 Visualization

### PyMOL Visualization
```bash
# Install PyMOL
conda install -c conda-forge pymol-open-source

# View NMDA + S-ketamine docking
pymol data/prepared/nmda/7eu8_clean.pdb \
      data/results/nmda/7EU8/S-ketamine/docked_poses.pdbqt

# In PyMOL console:
# show cartoon, 7eu8_clean
# show sticks, docked_poses
# color green, 7eu8_clean
# color cyan, docked_poses
```

### UCSF Chimera
```bash
# Download from: https://www.cgl.ucsf.edu/chimera/

# Open:
# 1. File → Open → data/prepared/nmda/7eu8_clean.pdb
# 2. File → Open → data/results/nmda/7EU8/S-ketamine/docked_poses.pdbqt
# 3. Tools → Structure Analysis → FindHBond
```

## 🐛 Troubleshooting

### Problem: "vina: command not found"
```bash
conda install -c conda-forge vina
vina --version  # Verify
```

### Problem: "No module named 'rdkit'"
```bash
pip install rdkit
# OR
conda install -c conda-forge rdkit
```

### Problem: "PDBQT conversion failed"
```bash
# Install Open Babel
conda install -c conda-forge openbabel
obabel --version  # Verify

# Alternative: Use cleaned PDB files
# Manual conversion: obabel input.pdb -O output.pdbqt -p 7.4
```

### Problem: "PDB download timeout"
- Check internet connection
- Try again (PDB servers occasionally busy)
- Download manually from https://www.rcsb.org/structure/7EU8

### Problem: Docking takes too long
```bash
# Reduce exhaustiveness in config files
nano configs/nmda_targets.yaml
# Change: exhaustiveness: 32 → exhaustiveness: 16

# Or run single target at a time
```

## 💡 Tips for Success

1. **Start with NMDA only** (known positive control)
   - Verify pipeline works
   - Check binding site is correct
   - Should get good affinity (-8 to -6 kcal/mol)

2. **Use high exhaustiveness for final results**
   - Test: exhaustiveness = 8-16 (fast)
   - Publication: exhaustiveness = 32 (thorough)

3. **Check binding sites**
   - Review PDB structures in viewer
   - Verify binding site coordinates make sense
   - Use auto_detect: true when co-crystallized ligand present

4. **Multiple structures per target**
   - Different conformations
   - Cross-validation
   - More confidence in results

5. **Compare enantiomers**
   - S-ketamine should show better binding
   - Validates stereochemistry handling

## 📚 Next Steps After Pipeline

1. **Validate Top Hits**
   - Molecular dynamics simulations
   - Binding free energy calculations (MM-PBSA)
   - Experimental validation

2. **Publication-Quality Figures**
   - PyMOL ray tracing
   - Interaction diagrams (LigPlot+)
   - Binding site analysis

3. **Extended Analysis**
   - Residue interaction analysis
   - Pharmacophore modeling
   - ADMET prediction

## 🆘 Need Help?

1. Check main `README.md` for detailed documentation
2. Review log files in `data/results/`
3. Verify all dependencies: `conda list`
4. Test individual steps separately

## 📊 Example Output

```
=======================================================================
OVERALL SUMMARY - KETAMINE DOCKING STUDY
=======================================================================

Best Binding Affinities by Target:

NMDA: -7.52 kcal/mol
  (Structure: 7EU8, Ligand: S-ketamine)

EGFR: -5.31 kcal/mol
  (Structure: 4G5J, Ligand: S-ketamine)

CSNK1D: -4.89 kcal/mol
  (Structure: 6GZM, Ligand: racemic-ketamine)

=======================================================================
TARGET RANKING BY BINDING AFFINITY
=======================================================================

1. NMDA: -7.52 kcal/mol
   Strong (Good binding - potentially significant interaction)

2. EGFR: -5.31 kcal/mol
   Weak (Weak binding - questionable biological relevance)

3. CSNK1D: -4.89 kcal/mol
   Very Weak (Very weak/no significant binding)
```

---

**Quick Reference:**
- 🔬 Full pipeline: `python run_pipeline.py --all`
- 📊 Results location: `data/results/reports/`
- ⚙️ Config files: `configs/*.yaml`
- 🆘 Troubleshooting: See main `README.md`
