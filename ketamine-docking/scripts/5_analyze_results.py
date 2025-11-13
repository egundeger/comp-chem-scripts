#!/usr/bin/env python3
"""
Docking Results Analysis and Reporting
Analyzes AutoDock Vina results and generates comprehensive reports
"""

import os
import sys
import json
import yaml
from pathlib import Path
from datetime import datetime
import pandas as pd

# Define project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "data" / "results"
CONFIG_DIR = PROJECT_ROOT / "configs"


def load_results():
    """Load docking results from JSON file"""
    results_file = RESULTS_DIR / "all_results.json"

    if not results_file.exists():
        print(f"✗ Results file not found: {results_file}")
        print("  Please run 4_run_docking.py first")
        return None

    try:
        with open(results_file, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"✗ Error loading results: {e}")
        return None


def load_config(target_name):
    """Load target configuration"""
    config_file = CONFIG_DIR / f"{target_name}_targets.yaml"

    if not config_file.exists():
        return None

    try:
        with open(config_file, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"⚠ Error loading config for {target_name}: {e}")
        return None


def create_summary_table(results):
    """Create summary table of all docking results"""

    data = []

    for target_name, target_results in results.items():
        for key, result in target_results.items():
            data.append({
                'Target': target_name.upper(),
                'PDB ID': result['pdb_id'].upper(),
                'Ligand': result['ligand'],
                'Best Affinity (kcal/mol)': result['best_affinity'],
                'Number of Modes': len(result.get('all_modes', []))
            })

    df = pd.DataFrame(data)
    df = df.sort_values(['Target', 'Best Affinity (kcal/mol)'])

    return df


def interpret_binding_affinity(affinity, target_name):
    """
    Interpret binding affinity score

    Args:
        affinity: Binding affinity in kcal/mol
        target_name: Target protein name

    Returns:
        Interpretation string
    """
    if affinity <= -9.0:
        strength = "Very Strong"
        comment = "Excellent binding - likely biologically relevant"
    elif affinity <= -8.0:
        strength = "Strong"
        comment = "Good binding - potentially significant interaction"
    elif affinity <= -7.0:
        strength = "Moderate"
        comment = "Moderate binding - may be relevant in context"
    elif affinity <= -6.0:
        strength = "Weak"
        comment = "Weak binding - questionable biological relevance"
    else:
        strength = "Very Weak"
        comment = "Very weak/no significant binding"

    return f"{strength} ({comment})"


def generate_target_report(target_name, target_results, config):
    """Generate detailed report for a target"""

    report = []
    report.append("=" * 70)
    report.append(f"TARGET: {target_name.upper()}")
    report.append("=" * 70)

    if config:
        report.append(f"\nDescription: {config.get('description', 'N/A')}")
        report.append(f"Priority: {config.get('priority', 'N/A')}")

        expected = config.get('expected_results', {})
        if expected:
            report.append(f"\n--- Expected Results ---")
            affinity_range = expected.get('binding_affinity_range', [])
            if affinity_range:
                report.append(f"Expected affinity range: {affinity_range[0]} to {affinity_range[1]} kcal/mol")

    report.append(f"\n--- Docking Results ---")

    # Group by PDB structure
    pdb_groups = {}
    for key, result in target_results.items():
        pdb_id = result['pdb_id']
        if pdb_id not in pdb_groups:
            pdb_groups[pdb_id] = []
        pdb_groups[pdb_id].append(result)

    for pdb_id, results in sorted(pdb_groups.items()):
        report.append(f"\nStructure: {pdb_id.upper()}")

        # Get structure description from config
        if config and 'structures' in config:
            struct_info = config['structures'].get(pdb_id, {})
            desc = struct_info.get('description', '')
            if desc:
                report.append(f"  Description: {desc}")

        for result in results:
            ligand = result['ligand']
            affinity = result['best_affinity']

            report.append(f"\n  Ligand: {ligand}")
            report.append(f"  Best binding affinity: {affinity:.2f} kcal/mol")
            report.append(f"  Interpretation: {interpret_binding_affinity(affinity, target_name)}")

            # Show top 3 modes
            all_modes = result.get('all_modes', [])
            if len(all_modes) > 1:
                report.append(f"  Top 3 binding modes:")
                for i, (mode, aff, rmsd_lb, rmsd_ub) in enumerate(all_modes[:3], 1):
                    report.append(f"    Mode {mode}: {aff:.2f} kcal/mol (RMSD: {rmsd_lb:.2f})")

    # Add interpretation based on config
    if config and 'expected_results' in config:
        expected = config['expected_results']
        interpretation = expected.get('interpretation', {})

        if interpretation:
            report.append(f"\n--- Biological Interpretation ---")

            # Determine overall binding strength
            best_affinity = min([r['best_affinity'] for r in target_results.values()])

            if best_affinity <= -7.0:
                interp_key = 'positive'
            elif best_affinity <= -5.0:
                interp_key = 'weak'
            else:
                interp_key = 'negative'

            if interp_key in interpretation:
                report.append(f"{interpretation[interp_key]}")

        context = expected.get('study_context', [])
        if context:
            report.append(f"\n--- Study Context ---")
            for item in context:
                report.append(f"• {item}")

    report.append("")
    return "\n".join(report)


def generate_overall_summary(results):
    """Generate overall summary across all targets"""

    summary = []
    summary.append("=" * 70)
    summary.append("OVERALL SUMMARY - KETAMINE DOCKING STUDY")
    summary.append("=" * 70)
    summary.append("")

    # Best results for each target
    summary.append("Best Binding Affinities by Target:")
    summary.append("")

    target_best = {}
    for target_name, target_results in sorted(results.items()):
        best_affinity = min([r['best_affinity'] for r in target_results.values()])
        best_result = [r for r in target_results.values() if r['best_affinity'] == best_affinity][0]

        target_best[target_name] = {
            'affinity': best_affinity,
            'pdb_id': best_result['pdb_id'],
            'ligand': best_result['ligand']
        }

        summary.append(f"{target_name.upper()}: {best_affinity:.2f} kcal/mol")
        summary.append(f"  (Structure: {best_result['pdb_id'].upper()}, Ligand: {best_result['ligand']})")
        summary.append("")

    # Ranking
    summary.append("=" * 70)
    summary.append("TARGET RANKING BY BINDING AFFINITY")
    summary.append("=" * 70)
    summary.append("")

    ranked = sorted(target_best.items(), key=lambda x: x[1]['affinity'])

    for i, (target, info) in enumerate(ranked, 1):
        summary.append(f"{i}. {target.upper()}: {info['affinity']:.2f} kcal/mol")
        summary.append(f"   {interpret_binding_affinity(info['affinity'], target)}")
        summary.append("")

    # Key findings
    summary.append("=" * 70)
    summary.append("KEY FINDINGS")
    summary.append("=" * 70)
    summary.append("")

    # NMDA-specific
    if 'nmda' in target_best:
        nmda_affinity = target_best['nmda']['affinity']
        summary.append("1. NMDA Receptor (Primary Target):")
        if nmda_affinity <= -7.0:
            summary.append("   ✓ Strong binding confirmed - consistent with known mechanism")
        elif nmda_affinity <= -6.0:
            summary.append("   ○ Moderate binding - expected for channel blocker")
        else:
            summary.append("   ⚠ Weaker than expected - check binding site definition")
        summary.append("")

    # EGFR-specific
    if 'egfr' in target_best:
        egfr_affinity = target_best['egfr']['affinity']
        summary.append("2. EGFR (EGF Downregulation Target):")
        if egfr_affinity <= -7.0:
            summary.append("   ✓ Direct binding possible - may explain EGF reduction")
        elif egfr_affinity <= -5.0:
            summary.append("   ○ Weak binding - EGF effects likely indirect")
        else:
            summary.append("   ✗ No significant binding - indirect mechanism confirmed")
        summary.append("")

    # CSNK1D-specific
    if 'csnk1d' in target_best:
        csnk1d_affinity = target_best['csnk1d']['affinity']
        summary.append("3. CSNK1D (Wnt Pathway Target):")
        if csnk1d_affinity <= -7.0:
            summary.append("   ✓ Direct inhibition possible - may affect Wnt signaling")
        elif csnk1d_affinity <= -5.0:
            summary.append("   ○ Weak binding - indirect modulation likely")
        else:
            summary.append("   ✗ No direct binding - upstream regulation suggested")
        summary.append("")

    summary.append("=" * 70)
    summary.append("RECOMMENDATIONS")
    summary.append("=" * 70)
    summary.append("")
    summary.append("1. Validate top-scoring poses with MD simulations")
    summary.append("2. Perform experimental binding assays for verification")
    summary.append("3. Investigate indirect mechanisms for weak/no binding targets")
    summary.append("4. Consider additional crystal structures if available")
    summary.append("5. Analyze key residue interactions in detail")
    summary.append("")

    return "\n".join(summary)


def save_excel_report(df, results, output_file):
    """Save comprehensive Excel report"""
    try:
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Summary sheet
            df.to_excel(writer, sheet_name='Summary', index=False)

            # Individual target sheets
            for target_name, target_results in results.items():
                target_data = []
                for key, result in target_results.items():
                    for mode_num, (mode, affinity, rmsd_lb, rmsd_ub) in enumerate(result.get('all_modes', []), 1):
                        target_data.append({
                            'PDB ID': result['pdb_id'].upper(),
                            'Ligand': result['ligand'],
                            'Mode': mode,
                            'Affinity (kcal/mol)': affinity,
                            'RMSD l.b.': rmsd_lb,
                            'RMSD u.b.': rmsd_ub
                        })

                if target_data:
                    target_df = pd.DataFrame(target_data)
                    sheet_name = target_name.upper()[:31]  # Excel sheet name limit
                    target_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"✓ Excel report saved: {output_file}")
        return True

    except Exception as e:
        print(f"⚠ Could not save Excel report: {e}")
        return False


def main():
    """Main execution"""
    print("=" * 70)
    print("KETAMINE DOCKING PIPELINE - Results Analysis")
    print("=" * 70)
    print()

    # Load results
    results = load_results()
    if not results:
        sys.exit(1)

    print(f"Loaded results for {len(results)} targets")
    print()

    # Create summary table
    df = create_summary_table(results)

    # Print summary table
    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print()
    print(df.to_string(index=False))
    print()

    # Generate reports
    report_dir = RESULTS_DIR / "reports"
    report_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Overall summary
    overall_summary = generate_overall_summary(results)
    print(overall_summary)

    overall_file = report_dir / f"overall_summary_{timestamp}.txt"
    with open(overall_file, 'w') as f:
        f.write(overall_summary)
    print(f"✓ Overall summary saved: {overall_file}")

    # Individual target reports
    for target_name, target_results in results.items():
        config = load_config(target_name)
        report = generate_target_report(target_name, target_results, config)

        target_file = report_dir / f"{target_name}_report_{timestamp}.txt"
        with open(target_file, 'w') as f:
            f.write(report)
        print(f"✓ {target_name.upper()} report saved: {target_file}")

    # Save Excel report
    excel_file = report_dir / f"docking_results_{timestamp}.xlsx"
    save_excel_report(df, results, excel_file)

    # Save summary CSV
    csv_file = report_dir / f"summary_{timestamp}.csv"
    df.to_csv(csv_file, index=False)
    print(f"✓ CSV summary saved: {csv_file}")

    print()
    print("=" * 70)
    print("ANALYSIS COMPLETE")
    print("=" * 70)
    print(f"Reports directory: {report_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
