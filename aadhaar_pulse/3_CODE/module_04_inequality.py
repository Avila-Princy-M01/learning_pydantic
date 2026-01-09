"""
AADHAAR PULSE - Module 04: Digital Inclusion Inequality Index
==============================================================
Measure digital divide across regions by analyzing activity patterns.

Key Insight: Districts with low activity across ALL datasets = systematically underserved
Biometric updates require physical visits, demographic can be remote - ratio reveals access gaps.

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')


def calculate_digital_inclusion_index(enrol_df, demo_df, bio_df, level='district'):
    """Calculate Digital Inclusion Index for each region."""
    
    group_cols = ['state'] if level == 'state' else ['state', 'district']
    
    # Aggregate all datasets
    enrol_agg = enrol_df.groupby(group_cols).agg({'total_enrolments': 'sum'}).reset_index()
    demo_agg = demo_df.groupby(group_cols).agg({'total_demo_updates': 'sum'}).reset_index()
    bio_agg = bio_df.groupby(group_cols).agg({'total_bio_updates': 'sum'}).reset_index()
    
    # Merge
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer')
    merged = merged.merge(bio_agg, on=group_cols, how='outer').fillna(0)
    
    # Calculate activity scores (normalized 0-100)
    merged['enrol_score'] = (merged['total_enrolments'] / merged['total_enrolments'].max()) * 100
    merged['demo_score'] = (merged['total_demo_updates'] / merged['total_demo_updates'].max()) * 100
    merged['bio_score'] = (merged['total_bio_updates'] / merged['total_bio_updates'].max()) * 100
    
    # Bio-to-Demo ratio (physical vs remote access indicator)
    merged['physical_access_ratio'] = np.where(
        merged['total_demo_updates'] > 0,
        merged['total_bio_updates'] / merged['total_demo_updates'],
        0
    )
    
    # Digital Inclusion Index (higher = better inclusion)
    merged['digital_inclusion_index'] = (
        merged['enrol_score'] * 0.3 +
        merged['demo_score'] * 0.35 +
        merged['bio_score'] * 0.35
    )
    
    # Digital Divide Score (higher = more excluded)
    merged['digital_divide_score'] = 100 - merged['digital_inclusion_index']
    
    # Classify regions
    def classify_inclusion(score):
        if score >= 70: return 'WELL_CONNECTED'
        elif score >= 50: return 'MODERATE'
        elif score >= 30: return 'UNDERSERVED'
        else: return 'SEVERELY_EXCLUDED'
    
    merged['inclusion_category'] = merged['digital_inclusion_index'].apply(classify_inclusion)
    
    return merged


def identify_excluded_regions(enrol_df, demo_df, bio_df, top_n=50):
    """Identify most digitally excluded regions."""
    inclusion_df = calculate_digital_inclusion_index(enrol_df, demo_df, bio_df, level='district')
    return inclusion_df.nsmallest(top_n, 'digital_inclusion_index')


def generate_inequality_summary(enrol_df, demo_df, bio_df):
    """Generate digital inequality summary."""
    
    state_inclusion = calculate_digital_inclusion_index(enrol_df, demo_df, bio_df, level='state')
    district_inclusion = calculate_digital_inclusion_index(enrol_df, demo_df, bio_df, level='district')
    excluded = identify_excluded_regions(enrol_df, demo_df, bio_df, top_n=10)
    
    return {
        'avg_inclusion_index': district_inclusion['digital_inclusion_index'].mean(),
        'inclusion_by_category': district_inclusion['inclusion_category'].value_counts().to_dict(),
        'most_excluded_districts': excluded[['state', 'district', 'digital_divide_score']].to_dict('records'),
        'most_included_states': state_inclusion.nlargest(5, 'digital_inclusion_index')[['state', 'digital_inclusion_index']].to_dict('records'),
        'least_included_states': state_inclusion.nsmallest(5, 'digital_inclusion_index')[['state', 'digital_inclusion_index']].to_dict('records')
    }


def print_inequality_report(summary):
    """Print digital inequality report."""
    print("\n" + "="*60)
    print("⚖️ DIGITAL INCLUSION INEQUALITY INDEX")
    print("="*60)
    
    print(f"\n📊 OVERALL")
    print(f"   Average Inclusion Index: {summary['avg_inclusion_index']:.1f}/100")
    
    print(f"\n📈 CATEGORY BREAKDOWN")
    for cat, count in summary['inclusion_by_category'].items():
        emoji = {'WELL_CONNECTED': '🟢', 'MODERATE': '🟡', 'UNDERSERVED': '🟠', 'SEVERELY_EXCLUDED': '🔴'}.get(cat, '⚪')
        print(f"   {emoji} {cat}: {count} districts")
    
    print(f"\n🔴 MOST EXCLUDED DISTRICTS")
    for d in summary['most_excluded_districts'][:5]:
        print(f"   • {d['district']}, {d['state']}: Divide Score {d['digital_divide_score']:.1f}")
    
    print("\n" + "="*60)
