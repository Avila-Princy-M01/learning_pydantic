"""
AADHAAR PULSE - Module 02: Anomaly Detection (Ghost Districts)
===============================================================
Detect suspicious patterns that may indicate fraud, system errors,
or unusual activity in Aadhaar enrolments and updates.

Key Insight: Districts with high enrolments but zero/minimal subsequent
updates are "Ghost Districts" - potential fraud or data quality issues.

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


def calculate_anomaly_scores(enrol_df, demo_df, bio_df, level='district'):
    """
    Calculate multiple anomaly scores for each region.
    
    Methods used:
    1. Z-score based outlier detection
    2. Isolation Forest
    3. Ratio-based anomaly detection
    
    Returns:
    --------
    pd.DataFrame
        Regions with anomaly scores and classifications
    """
    
    if level == 'state':
        group_cols = ['state']
    else:
        group_cols = ['state', 'district']
    
    # Aggregate all datasets
    enrol_agg = enrol_df.groupby(group_cols).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    demo_agg = demo_df.groupby(group_cols).agg({
        'total_demo_updates': 'sum'
    }).reset_index()
    
    bio_agg = bio_df.groupby(group_cols).agg({
        'total_bio_updates': 'sum'
    }).reset_index()
    
    # Merge all
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer')
    merged = merged.merge(bio_agg, on=group_cols, how='outer')
    merged = merged.fillna(0)
    
    # Calculate derived metrics
    merged['total_updates'] = merged['total_demo_updates'] + merged['total_bio_updates']
    merged['update_enrol_ratio'] = np.where(
        merged['total_enrolments'] > 0,
        merged['total_updates'] / merged['total_enrolments'],
        0
    )
    merged['bio_demo_ratio'] = np.where(
        merged['total_demo_updates'] > 0,
        merged['total_bio_updates'] / merged['total_demo_updates'],
        0
    )
    
    # METHOD 1: Z-Score Anomaly Detection
    for col in ['total_enrolments', 'total_updates', 'update_enrol_ratio']:
        z_scores = np.abs(stats.zscore(merged[col].fillna(0)))
        merged[f'{col}_zscore'] = z_scores
    
    merged['zscore_anomaly'] = (
        (merged['total_enrolments_zscore'] > 2.5) |
        (merged['total_updates_zscore'] > 2.5) |
        (merged['update_enrol_ratio_zscore'] > 2.5)
    ).astype(int)
    
    # METHOD 2: Isolation Forest
    features = ['total_enrolments', 'total_updates', 'update_enrol_ratio', 'bio_demo_ratio']
    X = merged[features].fillna(0)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    iso_forest = IsolationForest(contamination=0.1, random_state=42)
    merged['isolation_forest_anomaly'] = (iso_forest.fit_predict(X_scaled) == -1).astype(int)
    merged['isolation_forest_score'] = -iso_forest.score_samples(X_scaled)
    
    # METHOD 3: Ghost District Detection
    # High enrolments + Very low updates = Ghost District
    enrol_threshold = merged['total_enrolments'].quantile(0.5)
    update_ratio_threshold = merged['update_enrol_ratio'].quantile(0.1)
    
    merged['ghost_district'] = (
        (merged['total_enrolments'] > enrol_threshold) &
        (merged['update_enrol_ratio'] < update_ratio_threshold)
    ).astype(int)
    
    # COMBINED ANOMALY SCORE (0-100)
    merged['anomaly_score'] = (
        merged['zscore_anomaly'] * 25 +
        merged['isolation_forest_anomaly'] * 25 +
        merged['ghost_district'] * 30 +
        (merged['isolation_forest_score'] / merged['isolation_forest_score'].max()) * 20
    ).clip(0, 100)
    
    # Classify anomaly type
    def classify_anomaly(row):
        if row['anomaly_score'] >= 70:
            return 'CRITICAL'
        elif row['anomaly_score'] >= 50:
            return 'HIGH'
        elif row['anomaly_score'] >= 30:
            return 'MEDIUM'
        elif row['anomaly_score'] >= 10:
            return 'LOW'
        else:
            return 'NORMAL'
    
    merged['anomaly_level'] = merged.apply(classify_anomaly, axis=1)
    
    return merged


def detect_ghost_districts(enrol_df, demo_df, bio_df, top_n=50):
    """
    Identify Ghost Districts - areas with suspicious enrolment patterns.
    
    Ghost District Criteria:
    - High enrolments relative to median
    - Very low or zero subsequent updates
    - Unusual age distribution
    
    Returns:
    --------
    pd.DataFrame
        Top Ghost Districts with risk scores
    """
    
    anomaly_df = calculate_anomaly_scores(enrol_df, demo_df, bio_df, level='district')
    
    ghost_districts = anomaly_df[anomaly_df['ghost_district'] == 1].copy()
    
    # Calculate additional risk factors
    ghost_districts['risk_score'] = (
        ghost_districts['anomaly_score'] * 0.4 +
        (1 - ghost_districts['update_enrol_ratio']) * 30 +
        ghost_districts['isolation_forest_score'] / ghost_districts['isolation_forest_score'].max() * 30
    )
    
    # Estimate potential fraud value (simplified)
    avg_enrol_per_person = 1  # Assume 1 enrolment = 1 person
    cost_per_fraudulent_id = 50000  # Estimated cost of fraudulent ID misuse in INR
    ghost_districts['estimated_fraud_risk_inr'] = (
        ghost_districts['total_enrolments'] * 
        (1 - ghost_districts['update_enrol_ratio']) * 
        cost_per_fraudulent_id * 0.01  # Assume 1% fraud rate
    )
    
    return ghost_districts.nlargest(top_n, 'risk_score')


def detect_temporal_anomalies(enrol_df, demo_df, bio_df):
    """
    Detect anomalies in time series patterns.
    
    Looks for:
    - Sudden spikes in activity
    - Unusual drops (potential system issues)
    - Seasonal anomalies
    
    Returns:
    --------
    pd.DataFrame
        Daily/weekly data with anomaly flags
    """
    
    # Aggregate by date
    enrol_daily = enrol_df.groupby('date').agg({
        'total_enrolments': 'sum'
    }).reset_index()
    
    demo_daily = demo_df.groupby('date').agg({
        'total_demo_updates': 'sum'
    }).reset_index()
    
    bio_daily = bio_df.groupby('date').agg({
        'total_bio_updates': 'sum'
    }).reset_index()
    
    # Merge
    merged = enrol_daily.merge(demo_daily, on='date', how='outer')
    merged = merged.merge(bio_daily, on='date', how='outer')
    merged = merged.fillna(0).sort_values('date')
    
    # Calculate rolling statistics
    window = 7  # 7-day rolling window
    for col in ['total_enrolments', 'total_demo_updates', 'total_bio_updates']:
        merged[f'{col}_rolling_mean'] = merged[col].rolling(window=window, min_periods=1).mean()
        merged[f'{col}_rolling_std'] = merged[col].rolling(window=window, min_periods=1).std()
        
        # Z-score relative to rolling window
        merged[f'{col}_anomaly'] = np.abs(
            (merged[col] - merged[f'{col}_rolling_mean']) / 
            (merged[f'{col}_rolling_std'] + 1)
        ) > 3
    
    # Combined temporal anomaly
    merged['temporal_anomaly'] = (
        merged['total_enrolments_anomaly'] |
        merged['total_demo_updates_anomaly'] |
        merged['total_bio_updates_anomaly']
    ).astype(int)
    
    return merged


def detect_ratio_anomalies(enrol_df, demo_df, bio_df, level='district'):
    """
    Detect anomalies based on unusual ratios between datasets.
    
    Anomalous patterns:
    - Very high biometric updates but low demographic (unusual)
    - Very high child enrolments but low adult (unusual family structure)
    - Zero updates for extended periods after enrolment
    """
    
    if level == 'state':
        group_cols = ['state']
    else:
        group_cols = ['state', 'district']
    
    # Aggregate
    enrol_agg = enrol_df.groupby(group_cols).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    demo_agg = demo_df.groupby(group_cols).agg({
        'total_demo_updates': 'sum',
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    
    bio_agg = bio_df.groupby(group_cols).agg({
        'total_bio_updates': 'sum',
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    
    # Merge
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer')
    merged = merged.merge(bio_agg, on=group_cols, how='outer')
    merged = merged.fillna(0)
    
    # Calculate ratios
    merged['child_adult_enrol_ratio'] = np.where(
        merged['age_18_greater'] > 0,
        (merged['age_0_5'] + merged['age_5_17']) / merged['age_18_greater'],
        0
    )
    
    merged['bio_demo_ratio'] = np.where(
        merged['total_demo_updates'] > 0,
        merged['total_bio_updates'] / merged['total_demo_updates'],
        0
    )
    
    # Flag anomalies
    merged['unusual_age_distribution'] = (
        merged['child_adult_enrol_ratio'] > merged['child_adult_enrol_ratio'].quantile(0.95)
    ).astype(int)
    
    merged['unusual_bio_demo_ratio'] = (
        (merged['bio_demo_ratio'] > merged['bio_demo_ratio'].quantile(0.95)) |
        (merged['bio_demo_ratio'] < merged['bio_demo_ratio'].quantile(0.05))
    ).astype(int)
    
    merged['ratio_anomaly_count'] = (
        merged['unusual_age_distribution'] + merged['unusual_bio_demo_ratio']
    )
    
    return merged


def generate_anomaly_summary(enrol_df, demo_df, bio_df):
    """
    Generate comprehensive anomaly detection summary.
    """
    
    anomaly_df = calculate_anomaly_scores(enrol_df, demo_df, bio_df, level='district')
    ghost_districts = detect_ghost_districts(enrol_df, demo_df, bio_df, top_n=10)
    temporal_anomalies = detect_temporal_anomalies(enrol_df, demo_df, bio_df)
    
    summary = {
        'total_districts_analyzed': len(anomaly_df),
        
        # Anomaly breakdown
        'anomaly_by_level': anomaly_df['anomaly_level'].value_counts().to_dict(),
        
        # Ghost districts
        'ghost_district_count': anomaly_df['ghost_district'].sum(),
        'top_ghost_districts': ghost_districts[['state', 'district', 'risk_score', 
                                                  'estimated_fraud_risk_inr']].head(5).to_dict('records'),
        
        # Estimated fraud risk
        'total_estimated_fraud_risk_inr': ghost_districts['estimated_fraud_risk_inr'].sum(),
        
        # Temporal anomalies
        'temporal_anomaly_days': temporal_anomalies['temporal_anomaly'].sum(),
        'total_days_analyzed': len(temporal_anomalies),
        
        # Key metrics
        'avg_anomaly_score': anomaly_df['anomaly_score'].mean(),
        'max_anomaly_score': anomaly_df['anomaly_score'].max(),
        'critical_anomalies': len(anomaly_df[anomaly_df['anomaly_level'] == 'CRITICAL']),
        'high_anomalies': len(anomaly_df[anomaly_df['anomaly_level'] == 'HIGH'])
    }
    
    return summary


def print_anomaly_report(summary):
    """
    Print formatted anomaly detection report.
    """
    print("\n" + "="*60)
    print("👻 ANOMALY DETECTION REPORT (Ghost Districts)")
    print("="*60)
    
    print(f"\n📊 COVERAGE")
    print(f"   Districts Analyzed: {summary['total_districts_analyzed']}")
    print(f"   Days Analyzed: {summary['total_days_analyzed']}")
    
    print(f"\n⚠️ ANOMALY CLASSIFICATION")
    for level, count in summary['anomaly_by_level'].items():
        emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢', 'NORMAL': '⚪'}.get(level, '⚪')
        print(f"   {emoji} {level}: {count} districts")
    
    print(f"\n👻 GHOST DISTRICTS")
    print(f"   Total Ghost Districts: {summary['ghost_district_count']}")
    print(f"   Estimated Fraud Risk: ₹{summary['total_estimated_fraud_risk_inr']:,.0f}")
    
    if summary['top_ghost_districts']:
        print(f"\n🚨 TOP RISK DISTRICTS")
        for dist in summary['top_ghost_districts']:
            print(f"   • {dist['district']}, {dist['state']}")
            print(f"     Risk Score: {dist['risk_score']:.1f} | Est. Fraud: ₹{dist['estimated_fraud_risk_inr']:,.0f}")
    
    print(f"\n📅 TEMPORAL ANOMALIES")
    print(f"   Anomalous Days: {summary['temporal_anomaly_days']} / {summary['total_days_analyzed']}")
    
    print(f"\n📈 KEY METRICS")
    print(f"   Average Anomaly Score: {summary['avg_anomaly_score']:.1f}")
    print(f"   Maximum Anomaly Score: {summary['max_anomaly_score']:.1f}")
    print(f"   Critical Anomalies: {summary['critical_anomalies']}")
    print(f"   High Anomalies: {summary['high_anomalies']}")
    
    print("\n" + "="*60)
