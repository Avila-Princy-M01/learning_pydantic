"""
AADHAAR PULSE - Module 01: Migration Corridor Detection
========================================================
Detect population movement patterns by analyzing the relationship between
enrolments (new residents) and demographic updates (address changes).

Key Insight: High demographic updates + Low enrolments = People MOVING IN
            High enrolments + Low updates = New population establishing roots

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')


def calculate_migration_indicators(enrol_df, demo_df, level='district'):
    """
    Calculate migration indicators for each region.
    
    Parameters:
    -----------
    enrol_df : pd.DataFrame
        Cleaned enrolment data
    demo_df : pd.DataFrame
        Cleaned demographic update data
    level : str
        Aggregation level: 'state' or 'district'
    
    Returns:
    --------
    pd.DataFrame
        Migration indicators including:
        - update_enrol_ratio (UER): Ratio of updates to enrolments
        - migration_type: 'INFLOW', 'OUTFLOW', 'STABLE', 'NEW_SETTLEMENT'
        - migration_score: Intensity of migration activity
    """
    
    if level == 'state':
        group_cols = ['state']
    else:
        group_cols = ['state', 'district']
    
    # Aggregate enrolments
    enrol_agg = enrol_df.groupby(group_cols).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    # Aggregate demographic updates
    demo_agg = demo_df.groupby(group_cols).agg({
        'total_demo_updates': 'sum',
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    
    # Merge
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer').fillna(0)
    
    # Calculate Update-to-Enrolment Ratio (UER)
    merged['update_enrol_ratio'] = np.where(
        merged['total_enrolments'] > 0,
        merged['total_demo_updates'] / merged['total_enrolments'],
        0
    )
    
    # Calculate percentiles for classification
    uer_median = merged['update_enrol_ratio'].median()
    enrol_median = merged['total_enrolments'].median()
    
    # Classify migration type
    def classify_migration(row):
        uer = row['update_enrol_ratio']
        enrol = row['total_enrolments']
        
        if uer > uer_median * 1.5 and enrol < enrol_median:
            return 'INFLOW'  # High updates, low enrolments = people moving in
        elif uer < uer_median * 0.5 and enrol > enrol_median:
            return 'NEW_SETTLEMENT'  # Low updates, high enrolments = new population
        elif uer > uer_median * 1.5 and enrol > enrol_median:
            return 'HIGH_CHURN'  # High both = lots of movement
        elif uer < uer_median * 0.5 and enrol < enrol_median:
            return 'OUTFLOW'  # Low both = population leaving
        else:
            return 'STABLE'
    
    merged['migration_type'] = merged.apply(classify_migration, axis=1)
    
    # Calculate migration intensity score (0-100)
    merged['migration_score'] = (
        (merged['update_enrol_ratio'] / merged['update_enrol_ratio'].max()) * 50 +
        (merged['total_demo_updates'] / merged['total_demo_updates'].max()) * 50
    ).clip(0, 100)
    
    return merged


def detect_migration_corridors(enrol_df, demo_df, top_n=10):
    """
    Identify major migration corridors between states.
    
    A corridor is defined as a state pair where:
    - Source state has high outflow indicators
    - Destination state has high inflow indicators
    
    Returns:
    --------
    pd.DataFrame
        Top migration corridors with:
        - source_state, dest_state
        - corridor_strength: Estimated flow intensity
    """
    
    # Get state-level indicators
    state_indicators = calculate_migration_indicators(enrol_df, demo_df, level='state')
    
    # Identify source states (OUTFLOW or NEW_SETTLEMENT with high activity)
    sources = state_indicators[
        state_indicators['migration_type'].isin(['OUTFLOW', 'NEW_SETTLEMENT'])
    ].copy()
    sources['source_score'] = sources['total_enrolments'] / sources['total_enrolments'].sum()
    
    # Identify destination states (INFLOW or HIGH_CHURN)
    destinations = state_indicators[
        state_indicators['migration_type'].isin(['INFLOW', 'HIGH_CHURN'])
    ].copy()
    destinations['dest_score'] = destinations['total_demo_updates'] / destinations['total_demo_updates'].sum()
    
    # Create corridor pairs (simplified model)
    corridors = []
    for _, src in sources.iterrows():
        for _, dst in destinations.iterrows():
            if src['state'] != dst['state']:
                corridor_strength = src['source_score'] * dst['dest_score'] * 1000
                corridors.append({
                    'source_state': src['state'],
                    'dest_state': dst['state'],
                    'corridor_strength': corridor_strength,
                    'source_enrolments': src['total_enrolments'],
                    'dest_updates': dst['total_demo_updates']
                })
    
    corridors_df = pd.DataFrame(corridors)
    
    if len(corridors_df) > 0:
        corridors_df = corridors_df.nlargest(top_n, 'corridor_strength')
    
    return corridors_df


def calculate_monthly_migration_trends(enrol_df, demo_df):
    """
    Calculate monthly migration trends to identify seasonal patterns.
    
    Returns:
    --------
    pd.DataFrame
        Monthly migration metrics
    """
    
    # Monthly enrolments
    enrol_monthly = enrol_df.groupby(['year', 'month']).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    # Monthly demographic updates
    demo_monthly = demo_df.groupby(['year', 'month']).agg({
        'total_demo_updates': 'sum'
    }).reset_index()
    
    # Merge
    merged = enrol_monthly.merge(demo_monthly, on=['year', 'month'], how='outer').fillna(0)
    
    # Create date column
    merged['date'] = pd.to_datetime(merged[['year', 'month']].assign(day=1))
    
    # Calculate UER
    merged['update_enrol_ratio'] = np.where(
        merged['total_enrolments'] > 0,
        merged['total_demo_updates'] / merged['total_enrolments'],
        0
    )
    
    # Calculate month-over-month change
    merged['enrol_change'] = merged['total_enrolments'].pct_change() * 100
    merged['update_change'] = merged['total_demo_updates'].pct_change() * 100
    
    return merged.sort_values('date')


def get_top_migration_districts(enrol_df, demo_df, migration_type='INFLOW', top_n=20):
    """
    Get top districts by migration type.
    
    Parameters:
    -----------
    migration_type : str
        One of: 'INFLOW', 'OUTFLOW', 'HIGH_CHURN', 'NEW_SETTLEMENT', 'STABLE'
    top_n : int
        Number of districts to return
    
    Returns:
    --------
    pd.DataFrame
        Top districts for the specified migration type
    """
    
    district_indicators = calculate_migration_indicators(enrol_df, demo_df, level='district')
    
    filtered = district_indicators[district_indicators['migration_type'] == migration_type]
    
    return filtered.nlargest(top_n, 'migration_score')


def generate_migration_summary(enrol_df, demo_df):
    """
    Generate a comprehensive migration summary.
    
    Returns:
    --------
    dict
        Summary statistics and key findings
    """
    
    state_indicators = calculate_migration_indicators(enrol_df, demo_df, level='state')
    district_indicators = calculate_migration_indicators(enrol_df, demo_df, level='district')
    corridors = detect_migration_corridors(enrol_df, demo_df, top_n=5)
    
    summary = {
        'total_states': len(state_indicators),
        'total_districts': len(district_indicators),
        
        # State-level breakdown
        'states_by_type': state_indicators['migration_type'].value_counts().to_dict(),
        
        # District-level breakdown
        'districts_by_type': district_indicators['migration_type'].value_counts().to_dict(),
        
        # Top inflow states
        'top_inflow_states': state_indicators[
            state_indicators['migration_type'] == 'INFLOW'
        ].nlargest(5, 'migration_score')[['state', 'migration_score']].to_dict('records'),
        
        # Top outflow states
        'top_outflow_states': state_indicators[
            state_indicators['migration_type'] == 'OUTFLOW'
        ].nlargest(5, 'migration_score')[['state', 'migration_score']].to_dict('records'),
        
        # Major corridors
        'major_corridors': corridors.to_dict('records') if len(corridors) > 0 else [],
        
        # Key metrics
        'avg_update_enrol_ratio': state_indicators['update_enrol_ratio'].mean(),
        'max_update_enrol_ratio': state_indicators['update_enrol_ratio'].max(),
        'total_demographic_updates': demo_df['total_demo_updates'].sum(),
        'total_enrolments': enrol_df['total_enrolments'].sum()
    }
    
    return summary


def print_migration_report(summary):
    """
    Print a formatted migration report.
    """
    print("\n" + "="*60)
    print("🚶 MIGRATION CORRIDOR ANALYSIS REPORT")
    print("="*60)
    
    print(f"\n📊 COVERAGE")
    print(f"   States Analyzed: {summary['total_states']}")
    print(f"   Districts Analyzed: {summary['total_districts']}")
    
    print(f"\n📈 OVERALL METRICS")
    print(f"   Total Enrolments: {summary['total_enrolments']:,.0f}")
    print(f"   Total Demographic Updates: {summary['total_demographic_updates']:,.0f}")
    print(f"   Average Update-to-Enrolment Ratio: {summary['avg_update_enrol_ratio']:.2f}")
    
    print(f"\n🗺️ STATE CLASSIFICATION")
    for mtype, count in summary['states_by_type'].items():
        print(f"   {mtype}: {count} states")
    
    print(f"\n🏙️ DISTRICT CLASSIFICATION")
    for mtype, count in summary['districts_by_type'].items():
        print(f"   {mtype}: {count} districts")
    
    if summary['top_inflow_states']:
        print(f"\n⬆️ TOP INFLOW STATES (People Moving In)")
        for item in summary['top_inflow_states']:
            print(f"   • {item['state']}: Score {item['migration_score']:.1f}")
    
    if summary['top_outflow_states']:
        print(f"\n⬇️ TOP OUTFLOW STATES (People Moving Out)")
        for item in summary['top_outflow_states']:
            print(f"   • {item['state']}: Score {item['migration_score']:.1f}")
    
    if summary['major_corridors']:
        print(f"\n🛤️ MAJOR MIGRATION CORRIDORS")
        for corridor in summary['major_corridors']:
            print(f"   • {corridor['source_state']} → {corridor['dest_state']}: "
                  f"Strength {corridor['corridor_strength']:.2f}")
    
    print("\n" + "="*60)
