# Ketamine Docking Pipeline - Example Use Cases

## Example 1: Complete First-Time Run

**Scenario:** You want to perform complete docking study for all three targets.

```bash
# 1. Setup environment
conda create -n ketamine-docking python=3.10 -y
conda activate ketamine-docking

# 2. Install dependencies
cd ketamine-docking
pip install -r requirements.txt
conda install -c conda-forge vina openbabel -y

# 3. Check dependencies
python check_dependencies.py

# 4. Run complete pipeline
python run_pipeline.py --all

# 5. View results
cat data/results/reports/overall_summary_*.txt
```

**Expected Output:**
- Downloaded 8 PDB structures (3 NMDA + 3 EGFR + 2 CSNK1D)
- Generated 3 ketamine forms (S, R, racemic)
- Performed ~24 docking calculations
- Generated comprehensive reports

**Time:** ~1-2 hours

---

## Example 2: Priority 1 Only (NMDA)

**Scenario:** You want to quickly test with NMDA receptor (known positive control).

```bash
# Method 1: Edit config before running (recommended)
# Edit scripts/1_download_structures.py - keep only NMDA target
# Edit scripts/4_run_docking.py - keep only NMDA in targets list

python run_pipeline.py --all

# Method 2: Run individual scripts
python scripts/1_download_structures.py  # Download all (or edit to NMDA only)
python scripts/2_prepare_ligand.py
python scripts/3_prepare_proteins.py
# Then manually run docking for NMDA only

cd data/prepared/nmda
vina --config <manual_config> --out results.pdbqt
```

**Expected Results:**
- 7EU8 (with S-ketamine): -7.5 to -8.0 kcal/mol ✓
- 4PE5: -6.5 to -7.5 kcal/mol
- 5IPR: -6.0 to -7.0 kcal/mol

**Time:** ~30 minutes

---

## Example 3: Re-docking with Different Parameters

**Scenario:** Initial docking complete, want to re-run with higher exhaustiveness.

```bash
# 1. Edit configuration files
nano configs/nmda_targets.yaml
# Change: exhaustiveness: 24 → exhaustiveness: 48
# Change: num_modes: 15 → num_modes: 30

# 2. Backup previous results (optional)
cp -r data/results data/results_backup

# 3. Re-run docking only
python run_pipeline.py --dock --analyze

# 4. Compare results
diff data/results_backup/reports/nmda_report_*.txt \
     data/results/reports/nmda_report_*.txt
```

**When to do this:**
- Initial results look promising
- Need more thorough search for publication
- Exploring alternative binding modes

---

## Example 4: Testing Single Structure

**Scenario:** Test 7EU8 (NMDA + ketamine crystal structure) as validation.

```bash
# 1. Create test directory
mkdir -p test_7eu8
cd test_7eu8

# 2. Download just 7EU8
python << EOF
from Bio.PDB import PDBList
pdb_list = PDBList()
pdb_list.retrieve_pdb_file('7EU8', pdir='.', file_format='pdb')
EOF

# 3. Prepare ligand (back in main directory)
cd ..
python scripts/2_prepare_ligand.py

# 4. Prepare 7EU8 only
python << EOF
from Bio.PDB import PDBParser, PDBIO, Select
import subprocess

class ProteinSelect(Select):
    def accept_residue(self, residue):
        return residue.get_id()[0] == ' '

parser = PDBParser(QUIET=True)
structure = parser.get_structure('7eu8', 'test_7eu8/pdb7eu8.ent')
io = PDBIO()
io.set_structure(structure)
io.save('test_7eu8/7eu8_clean.pdb', ProteinSelect())

# Convert to PDBQT
subprocess.run(['obabel', 'test_7eu8/7eu8_clean.pdb',
                '-O', 'test_7eu8/7eu8.pdbqt', '-xr'])
EOF

# 5. Create minimal Vina config
cat > test_7eu8/vina.conf << EOF
receptor = test_7eu8/7eu8.pdbqt
ligand = data/ligands/S-ketamine.pdbqt

center_x = 0.0
center_y = 0.0
center_z = 0.0

size_x = 25.0
size_y = 25.0
size_z = 25.0

exhaustiveness = 16
num_modes = 10

out = test_7eu8/docked.pdbqt
log = test_7eu8/vina.log
EOF

# 6. Run docking
vina --config test_7eu8/vina.conf

# 7. Check results
cat test_7eu8/vina.log
```

**Expected:** Should reproduce crystallographic pose with RMSD < 2Å

---

## Example 5: Comparing Enantiomers

**Scenario:** Verify S-ketamine binds better than R-ketamine.

```bash
# Run complete pipeline (generates both)
python run_pipeline.py --all

# Extract S vs R comparison
python << EOF
import json
import pandas as pd

with open('data/results/all_results.json', 'r') as f:
    results = json.load(f)

comparisons = []
for target, target_results in results.items():
    for key, result in target_results.items():
        pdb_id = result['pdb_id']
        ligand = result['ligand']
        affinity = result['best_affinity']

        comparisons.append({
            'Target': target,
            'PDB': pdb_id,
            'Ligand': ligand,
            'Affinity': affinity
        })

df = pd.DataFrame(comparisons)

# Compare S vs R for each structure
for target in df['Target'].unique():
    for pdb in df[df['Target'] == target]['PDB'].unique():
        subset = df[(df['Target'] == target) & (df['PDB'] == pdb)]

        s_ket = subset[subset['Ligand'] == 'S-ketamine']['Affinity'].values
        r_ket = subset[subset['Ligand'] == 'R-ketamine']['Affinity'].values

        if len(s_ket) > 0 and len(r_ket) > 0:
            diff = r_ket[0] - s_ket[0]
            better = "S-ketamine" if s_ket[0] < r_ket[0] else "R-ketamine"
            print(f"{target}/{pdb}: {better} better by {abs(diff):.2f} kcal/mol")
            print(f"  S-ket: {s_ket[0]:.2f}, R-ket: {r_ket[0]:.2f}")
EOF
```

**Expected:** S-ketamine should show 0.5-2 kcal/mol better binding than R-ketamine

---

## Example 6: Publication-Quality Run

**Scenario:** Final docking for publication with maximum settings.

```bash
# 1. Edit all config files for maximum exhaustiveness
for config in configs/*.yaml; do
    sed -i 's/exhaustiveness: [0-9]*/exhaustiveness: 64/' "$config"
    sed -i 's/num_modes: [0-9]*/num_modes: 30/' "$config"
done

# 2. Create dated results directory
DATE=$(date +%Y%m%d)
mkdir -p publication_results_$DATE

# 3. Run with maximum settings
python run_pipeline.py --all

# 4. Copy results
cp -r data/results/* publication_results_$DATE/

# 5. Generate supplementary files
python << EOF
import json
import pandas as pd

with open('data/results/all_results.json', 'r') as f:
    results = json.load(f)

# Create detailed supplementary table
supp_data = []
for target, target_results in results.items():
    for key, result in target_results.items():
        pdb_id = result['pdb_id']
        ligand = result['ligand']

        for mode, affinity, rmsd_lb, rmsd_ub in result.get('all_modes', []):
            supp_data.append({
                'Target': target.upper(),
                'PDB ID': pdb_id.upper(),
                'Ligand': ligand,
                'Mode': mode,
                'Binding Affinity (kcal/mol)': affinity,
                'RMSD l.b. (Å)': rmsd_lb,
                'RMSD u.b. (Å)': rmsd_ub
            })

df = pd.DataFrame(supp_data)
df = df.sort_values(['Target', 'PDB ID', 'Ligand', 'Binding Affinity (kcal/mol)'])

df.to_excel(f'publication_results_{DATE}/supplementary_table_all_modes.xlsx',
            index=False, engine='openpyxl')
df.to_csv(f'publication_results_{DATE}/supplementary_table_all_modes.csv',
          index=False)

print(f"Supplementary tables saved to publication_results_{DATE}/")
EOF
```

**Time:** 3-4 hours
**Output:** High-quality results suitable for publication

---

## Example 7: Adding Custom Target

**Scenario:** You want to dock ketamine to a new target (e.g., GABAAR).

```bash
# 1. Create new config
cat > configs/gabaar_targets.yaml << EOF
target_name: GABAAR
description: "GABA-A Receptor - Alternative ketamine target"
priority: 4

structures:
  6D6U:
    description: "GABA-A receptor alpha1-beta2-gamma2"
    pdb_id: "6D6U"
    binding_site:
      center_x: 0.0
      center_y: 0.0
      center_z: 0.0
      size_x: 30.0
      size_y: 30.0
      size_z: 30.0
      auto_detect: false
      manual_center:
        x: 100.0  # Adjust based on structure
        y: 100.0
        z: 50.0
    exhaustiveness: 24
    num_modes: 15

expected_results:
  binding_affinity_range: [-7.0, -5.0]
  interpretation:
    positive: "May contribute to anesthetic effects"
    negative: "Effects likely NMDA-mediated only"
EOF

# 2. Add to download script
# Edit scripts/1_download_structures.py
# Add to TARGETS dict:
# "GABAAR": {
#     "priority": 4,
#     "description": "GABA-A Receptor",
#     "structures": {"6D6U": "GABA-A receptor alpha1-beta2-gamma2"}
# }

# 3. Add to docking script
# Edit scripts/4_run_docking.py
# Add to targets list:
# ('gabaar', CONFIG_DIR / 'gabaar_targets.yaml')

# 4. Run pipeline
python run_pipeline.py --all
```

---

## Example 8: Batch Analysis

**Scenario:** Compare results across multiple docking runs.

```bash
# After running pipeline multiple times with different settings

python << EOF
import json
import pandas as pd
from pathlib import Path

# Load all result files
result_dirs = [
    'data/results',
    'data/results_high_exhaustiveness',
    'data/results_different_box'
]

all_comparisons = []

for result_dir in result_dirs:
    result_file = Path(result_dir) / 'all_results.json'
    if not result_file.exists():
        continue

    with open(result_file, 'r') as f:
        results = json.load(f)

    run_name = result_dir.split('/')[-1]

    for target, target_results in results.items():
        for key, result in target_results.items():
            all_comparisons.append({
                'Run': run_name,
                'Target': target,
                'PDB': result['pdb_id'],
                'Ligand': result['ligand'],
                'Best Affinity': result['best_affinity']
            })

df = pd.DataFrame(all_comparisons)

# Pivot table
pivot = df.pivot_table(
    values='Best Affinity',
    index=['Target', 'PDB', 'Ligand'],
    columns='Run',
    aggfunc='first'
)

print(pivot)
pivot.to_excel('comparison_across_runs.xlsx')
EOF
```

---

## Example 9: Quick Validation

**Scenario:** Verify pipeline is working correctly before full run.

```bash
# 1. Test with minimal settings
python << EOF
import yaml

for config_file in ['configs/nmda_targets.yaml']:
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)

    # Modify to minimal settings
    for structure in config['structures'].values():
        structure['exhaustiveness'] = 8
        structure['num_modes'] = 3

    # Keep only first structure
    first_key = list(config['structures'].keys())[0]
    config['structures'] = {first_key: config['structures'][first_key]}

    with open(config_file.replace('.yaml', '_test.yaml'), 'w') as f:
        yaml.dump(config, f)
EOF

# 2. Run fast test
# Edit scripts/4_run_docking.py to use *_test.yaml configs
python run_pipeline.py --all

# 3. Check if results look reasonable
cat data/results/reports/overall_summary_*.txt
```

**Time:** ~10 minutes
**Purpose:** Verify everything works before committing to long run

---

## Troubleshooting Examples

### Problem: Binding affinities too weak

```bash
# Check binding site coordinates
pymol data/prepared/nmda/7eu8_clean.pdb

# In PyMOL, identify binding site
# show surface
# zoom ligand  # if co-crystallized ligand present

# Update config with correct coordinates
nano configs/nmda_targets.yaml
```

### Problem: Docking fails for specific structure

```bash
# Check structure integrity
python << EOF
from Bio.PDB import PDBParser, PDBCheckWarnings
import warnings

warnings.simplefilter('ignore', PDBCheckWarnings)
parser = PDBParser()

structure = parser.get_structure('test', 'data/proteins/nmda/7eu8.pdb')

# Count atoms
n_atoms = sum(1 for atom in structure.get_atoms())
print(f"Total atoms: {n_atoms}")

# Check for issues
for model in structure:
    for chain in model:
        print(f"Chain {chain.id}: {len(chain)} residues")
EOF

# If issues found, try re-downloading
rm data/proteins/nmda/7eu8.pdb
python scripts/1_download_structures.py
```

---

These examples cover most common use cases. Adapt as needed for your specific research questions!
