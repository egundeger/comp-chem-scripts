# Ketamine Docking Pipeline

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/egundeger/comp-chem-scripts/blob/main/ketamine-docking/Ketamine_Docking_Colab.ipynb)

Comprehensive molecular docking pipeline for investigating ketamine interactions with multiple protein targets.

**🚀 Quick Start:**
- **Ketamine Docking** (no installation): [Open in Colab](https://colab.research.google.com/github/egundeger/comp-chem-scripts/blob/main/ketamine-docking/Ketamine_Docking_Colab.ipynb) | [Guide](README_COLAB.md)
- **FDA Drug Screening** (ZINC20): [Open in Colab](https://colab.research.google.com/github/egundeger/comp-chem-scripts/blob/main/ketamine-docking/ZINC_FDA_Screening_Colab.ipynb) | [Guide](README_ZINC_SCREENING.md)
- **Local Installation**: See instructions below

## 📚 Available Pipelines

### 1. Ketamine Docking Pipeline
Focused docking study for ketamine against NMDA, EGFR, and CSNK1D targets.
- Single ligand (ketamine enantiomers)
- Multiple protein structures per target
- Detailed binding site analysis
- Literature validation

### 2. ZINC20 FDA Drug Screening 🆕
Large-scale virtual screening of FDA approved drugs.
- 1000s of FDA approved compounds
- Automated ligand preparation
- Batch docking with ranking
- Hit validation workflow
- Drug repurposing applications

## Overview

This pipeline performs automated molecular docking studies to investigate ketamine binding to three priority targets:

### 🎯 Target Priority List

#### **Priority 1: NMDA Receptor** ⭐⭐⭐
- **Target:** NMDA receptor GluN2B subunit
- **Rationale:** Primary known target of ketamine, well-documented channel blocker mechanism
- **PDB Structures:**
  - `7EU8` - GluN1-GluN2B + S-ketamine complex (human) - gold standard
  - `4PE5` - GluN1a/GluN2B NMDA receptor
  - `5IPR` - GluN1/GluN2B NMDA receptor
- **Expected Results:** Strong binding affinity (-8 to -6 kcal/mol), key interactions with Leu643, Asn616

#### **Priority 2: EGFR** ⭐⭐
- **Target:** EGFR kinase domain
- **Rationale:** EGF expression significantly reduced in your study
- **PDB Structures:**
  - `4I24` - EGFR kinase domain (wild-type)
  - `4G5J` - EGFR kinase + inhibitor complex
  - `2GS6` - Active EGFR kinase domain
- **Expected Results:** Evaluates direct vs. indirect mechanism for EGF downregulation

#### **Priority 3: CSNK1D (Casein Kinase)** ⭐
- **Target:** Casein Kinase 1 Delta
- **Rationale:** Central role in Wnt/β-catenin pathway, downregulated in study
- **PDB Structures:**
  - `6GZM` - CSNK1D with inhibitor
  - `5OKS` - CSNK1D catalytic domain
- **Expected Results:** Investigates direct binding vs. upstream regulation

## Features

- ✅ Automated PDB structure download
- ✅ 3D ligand generation from SMILES (S-ketamine, R-ketamine, racemic)
- ✅ Protein structure preparation and cleaning
- ✅ AutoDock Vina molecular docking
- ✅ Comprehensive result analysis and reporting
- ✅ Excel/CSV export of results
- ✅ Literature-based binding site definitions

## Requirements

### Python Dependencies
```bash
pip install -r requirements.txt
```

### External Tools

**Required:**
- **AutoDock Vina** - For molecular docking
  ```bash
  conda install -c conda-forge vina
  ```
  Or download from: https://github.com/ccsb-scripps/AutoDock-Vina

**Optional (for PDBQT conversion):**
- **Open Babel** - For format conversion
  ```bash
  conda install -c conda-forge openbabel
  ```
- **MGLTools** - Alternative for PDBQT preparation
  - Download from: https://ccsb.scripps.edu/mgltools/

## Installation

1. **Clone or download this pipeline:**
   ```bash
   cd ketamine-docking
   ```

2. **Create conda environment (recommended):**
   ```bash
   conda create -n ketamine-docking python=3.10
   conda activate ketamine-docking
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   conda install -c conda-forge vina openbabel
   ```

4. **Verify installation:**
   ```bash
   vina --version
   obabel --version
   python -c "import rdkit; print(rdkit.__version__)"
   ```

## Usage

### Quick Start - Run Complete Pipeline

```bash
python run_pipeline.py --all
```

This will execute all steps:
1. Download PDB structures
2. Prepare ketamine ligand
3. Prepare protein structures
4. Run docking calculations
5. Analyze results

### Run Individual Steps

```bash
# Download structures only
python run_pipeline.py --download

# Prepare ligand and proteins
python run_pipeline.py --prepare-ligand --prepare-proteins

# Run docking and analysis
python run_pipeline.py --dock --analyze
```

### Advanced Usage

```bash
# Run from docking onwards (if structures already prepared)
python run_pipeline.py --from-dock

# Skip download if structures already available
python run_pipeline.py --all --skip-download

# Run individual scripts directly
python scripts/1_download_structures.py
python scripts/2_prepare_ligand.py
python scripts/3_prepare_proteins.py
python scripts/4_run_docking.py
python scripts/5_analyze_results.py
```

## Project Structure

```
ketamine-docking/
├── README.md                  # This file
├── requirements.txt           # Python dependencies
├── run_pipeline.py            # Master pipeline script
│
├── configs/                   # Target configurations
│   ├── nmda_targets.yaml      # NMDA receptor docking params
│   ├── egfr_targets.yaml      # EGFR docking params
│   └── csnk1d_targets.yaml    # CSNK1D docking params
│
├── scripts/                   # Pipeline scripts
│   ├── 1_download_structures.py    # PDB downloader
│   ├── 2_prepare_ligand.py         # Ketamine 3D structure
│   ├── 3_prepare_proteins.py       # Protein preparation
│   ├── 4_run_docking.py            # AutoDock Vina docking
│   └── 5_analyze_results.py        # Results analysis
│
└── data/                      # Data directory (created during run)
    ├── proteins/              # Downloaded PDB files
    │   ├── nmda/
    │   ├── egfr/
    │   └── csnk1d/
    ├── ligands/               # Ketamine structures
    │   ├── S-ketamine.pdb
    │   ├── R-ketamine.pdb
    │   └── racemic-ketamine.pdb
    ├── prepared/              # Prepared structures (PDBQT)
    │   ├── nmda/
    │   ├── egfr/
    │   └── csnk1d/
    └── results/               # Docking results
        ├── nmda/
        ├── egfr/
        ├── csnk1d/
        ├── all_results.json
        └── reports/
            ├── overall_summary_*.txt
            ├── nmda_report_*.txt
            ├── egfr_report_*.txt
            ├── csnk1d_report_*.txt
            ├── docking_results_*.xlsx
            └── summary_*.csv
```

## Understanding Results

### Binding Affinity Interpretation

AutoDock Vina reports binding affinity in kcal/mol (more negative = stronger binding):

| Affinity (kcal/mol) | Interpretation | Biological Relevance |
|---------------------|----------------|----------------------|
| ≤ -9.0 | Very Strong | Excellent binding, likely significant |
| -9.0 to -8.0 | Strong | Good binding, potentially important |
| -8.0 to -7.0 | Moderate | May be relevant in biological context |
| -7.0 to -6.0 | Weak | Questionable biological relevance |
| > -6.0 | Very Weak | Likely no significant interaction |

### Expected Results by Target

**NMDA Receptor:**
- Expected affinity: -8 to -6 kcal/mol
- Should show strong binding to channel blocker site
- Key interactions: Leu643, Asn616, Gln645

**EGFR:**
- If strong binding (< -7 kcal/mol): Suggests direct inhibition
- If weak binding (> -5 kcal/mol): EGF downregulation likely indirect

**CSNK1D:**
- Positive result: May directly affect Wnt signaling
- Negative result: Suggests upstream or indirect regulation

## Output Files

### Reports Directory
- `overall_summary_*.txt` - Complete summary across all targets
- `{target}_report_*.txt` - Detailed report for each target
- `docking_results_*.xlsx` - Excel spreadsheet with all modes
- `summary_*.csv` - CSV summary table
- `all_results.json` - Raw JSON data

### Docking Outputs (per target/structure/ligand)
- `docked_poses.pdbqt` - All docking poses
- `vina.log` - AutoDock Vina output log
- `vina_config.txt` - Docking parameters used

## Visualization

To visualize docking results:

### Using PyMOL
```bash
pymol data/prepared/nmda/7eu8_clean.pdb \
      data/results/nmda/7EU8/S-ketamine/docked_poses.pdbqt
```

### Using Chimera
1. Open protein: `data/prepared/nmda/7eu8_clean.pdb`
2. Open ligand: `data/results/nmda/7EU8/S-ketamine/docked_poses.pdbqt`
3. Analyze interactions using Tools > Structure Analysis

## Troubleshooting

### "AutoDock Vina not found"
```bash
conda install -c conda-forge vina
# Or download binary from GitHub
```

### "PDBQT conversion failed"
Install Open Babel or MGLTools:
```bash
conda install -c conda-forge openbabel
```

### "PDB download failed"
- Check internet connection
- PDB servers may be temporarily down
- Try downloading manually from https://www.rcsb.org

### "RDKit import error"
```bash
conda install -c conda-forge rdkit
```

### Low binding affinities across all targets
- Check binding site coordinates in config files
- Verify protein structures are complete
- Consider using different PDB structures
- Check ligand preparation (correct stereochemistry)

## Customization

### Adding New Targets

1. Create new config file in `configs/`:
   ```yaml
   target_name: MY_TARGET
   description: "Description here"
   priority: 4
   structures:
     XXXX:
       description: "Structure description"
       pdb_id: "XXXX"
       binding_site:
         center_x: 0.0
         center_y: 0.0
         center_z: 0.0
         size_x: 25.0
         size_y: 25.0
         size_z: 25.0
   ```

2. Add target to `scripts/1_download_structures.py` TARGETS dict
3. Update `scripts/4_run_docking.py` targets list

### Modifying Docking Parameters

Edit config YAML files:
- `exhaustiveness`: Search thoroughness (8-32, higher = better but slower)
- `num_modes`: Number of binding modes to generate (10-20)
- `size_x/y/z`: Search box dimensions (Å)

### Using Different Ligands

Modify `scripts/2_prepare_ligand.py`:
- Add new SMILES strings to KETAMINE_STRUCTURES dict
- Or provide your own PDB/MOL2 files in `data/ligands/`

## Citation

If you use this pipeline in your research, please cite:

**AutoDock Vina:**
- Eberhardt, J., Santos-Martins, D., Tillack, A.F., Forli, S. (2021). AutoDock Vina 1.2.0: New Docking Methods, Expanded Force Field, and Python Bindings. Journal of Chemical Information and Modeling.

**PDB Structures:**
- Cite specific PDB entries used (7EU8, 4PE5, etc.)

**RDKit:**
- RDKit: Open-source cheminformatics; http://www.rdkit.org

## References

### NMDA Receptor / Ketamine
- Zanos P, et al. (2018). Ketamine and ketamine metabolite pharmacology: insights into therapeutic mechanisms. Pharmacol Rev. 70(3):621-660.
- Structure 7EU8: Chou et al. (2022). NMDA receptor with S-ketamine. Nature Communications.

### EGFR
- Comprehensive EGFR structural biology at RCSB PDB
- Receptor tyrosine kinase inhibitor design

### CSNK1D / Wnt Signaling
- Casein kinase role in Wnt/β-catenin pathway
- Structural studies of CSNK1D inhibitors

## License

This pipeline is provided as-is for research and educational purposes.

## Support

For issues or questions:
1. Check troubleshooting section
2. Verify all dependencies are installed
3. Review log files in `data/results/`
4. Consult AutoDock Vina documentation: https://autodock-vina.readthedocs.io/

## Acknowledgments

- RCSB Protein Data Bank for structural data
- AutoDock Vina developers
- RDKit community
- BioPython developers

---

**Version:** 1.0
**Last Updated:** 2025-01-13
**Author:** Computational Chemistry Pipeline
