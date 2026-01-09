"""
AADHAAR PULSE - Modules 05-11: Advanced Analysis Suite
=======================================================
Combined module containing all advanced analysis functions.

Module 05: Life Event Velocity Analysis
Module 06: Crisis Early Warning System  
Module 07: Aadhaar Sentiment Index
Module 08: Cohort Tracking
Module 09: Policy Impact Analysis
Module 10: Economic Calendar Patterns
Module 11: Future Demand Equation

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# =============================================================================
# MODULE 05: LIFE EVENT VELOCITY ANALYSIS
# =============================================================================

def calculate_life_event_velocity(enrol_df, demo_df, bio_df, level='district'):
    """
    Track lifecycle: Enrolment → Demographic Update → Biometric Update
    Detect broken patterns where normal progression is disrupted.
    """
    group_cols = ['state'] if level == 'state' else ['state', 'district']
    
    enrol_agg = enrol_df.groupby(group_cols).agg({'total_enrolments': 'sum'}).reset_index()
    demo_agg = demo_df.groupby(group_cols).agg({'total_demo_updates': 'sum'}).reset_index()
    bio_agg = bio_df.groupby(group_cols).agg({'total_bio_updates': 'sum'}).reset_index()
    
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer')
    merged = merged.merge(bio_agg, on=group_cols, how='outer').fillna(0)
    
    # Calculate velocity metrics
    merged['demo_velocity'] = merged['total_demo_updates'] / (merged['total_enrolments'] + 1)
    merged['bio_velocity'] = merged['total_bio_updates'] / (merged['total_enrolments'] + 1)
    merged['lifecycle_completion'] = (merged['total_demo_updates'] + merged['total_bio_updates']) / (2 * merged['total_enrolments'] + 1)
    
    # Detect anomalies
    merged['broken_lifecycle'] = (
        (merged['bio_velocity'] > merged['demo_velocity'] * 2) |  # Bio without demo
        (merged['lifecycle_completion'] < 0.1)  # Very low completion
    ).astype(int)
    
    return merged


# =============================================================================
# MODULE 06: CRISIS EARLY WARNING SYSTEM
# =============================================================================

def detect_crisis_signals(enrol_df, demo_df, bio_df, sensitivity=2.5):
    """
    Detect potential crises through sudden changes in Aadhaar activity patterns.
    - Sudden spikes = mass displacement or emergency
    - Dead zones = disaster-struck areas
    """
    # Daily aggregation
    enrol_daily = enrol_df.groupby('date')['total_enrolments'].sum().reset_index()
    demo_daily = demo_df.groupby('date')['total_demo_updates'].sum().reset_index()
    bio_daily = bio_df.groupby('date')['total_bio_updates'].sum().reset_index()
    
    merged = enrol_daily.merge(demo_daily, on='date', how='outer')
    merged = merged.merge(bio_daily, on='date', how='outer').fillna(0).sort_values('date')
    
    merged['total_activity'] = merged['total_enrolments'] + merged['total_demo_updates'] + merged['total_bio_updates']
    
    # Rolling statistics
    merged['rolling_mean'] = merged['total_activity'].rolling(7, min_periods=1).mean()
    merged['rolling_std'] = merged['total_activity'].rolling(7, min_periods=1).std().fillna(1)
    
    # Z-score for anomaly detection
    merged['zscore'] = (merged['total_activity'] - merged['rolling_mean']) / (merged['rolling_std'] + 1)
    
    # Crisis classification
    def classify_alert(zscore):
        if zscore > sensitivity * 1.5: return 'RED'
        elif zscore > sensitivity: return 'ORANGE'
        elif zscore > sensitivity * 0.5: return 'YELLOW'
        elif zscore < -sensitivity: return 'DEAD_ZONE'
        else: return 'GREEN'
    
    merged['alert_level'] = merged['zscore'].apply(classify_alert)
    merged['is_crisis'] = merged['alert_level'].isin(['RED', 'ORANGE', 'DEAD_ZONE']).astype(int)
    
    return merged


def get_crisis_summary(enrol_df, demo_df, bio_df):
    """Generate crisis detection summary."""
    crisis_df = detect_crisis_signals(enrol_df, demo_df, bio_df)
    
    return {
        'total_days': len(crisis_df),
        'crisis_days': crisis_df['is_crisis'].sum(),
        'alert_breakdown': crisis_df['alert_level'].value_counts().to_dict(),
        'recent_alerts': crisis_df[crisis_df['is_crisis'] == 1].tail(5)[['date', 'alert_level', 'zscore']].to_dict('records')
    }


# =============================================================================
# MODULE 07: AADHAAR SENTIMENT INDEX
# =============================================================================

def calculate_sentiment_index(enrol_df, demo_df, bio_df, level='state'):
    """
    Calculate Aadhaar Sentiment Index - a composite well-being indicator.
    Components: Stability, Growth, Engagement, Crisis scores
    """
    group_cols = ['state'] if level == 'state' else ['state', 'district']
    
    # Aggregate
    enrol_agg = enrol_df.groupby(group_cols).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum'
    }).reset_index()
    
    demo_agg = demo_df.groupby(group_cols).agg({'total_demo_updates': 'sum'}).reset_index()
    bio_agg = bio_df.groupby(group_cols).agg({'total_bio_updates': 'sum'}).reset_index()
    
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer')
    merged = merged.merge(bio_agg, on=group_cols, how='outer').fillna(0)
    
    merged['total_activity'] = merged['total_enrolments'] + merged['total_demo_updates'] + merged['total_bio_updates']
    
    # Component scores (normalized 0-1)
    merged['stability_score'] = 1 - (merged['total_demo_updates'] / (merged['total_activity'] + 1))
    merged['growth_score'] = merged['age_0_5'] / (merged['total_enrolments'] + 1)
    merged['engagement_score'] = (merged['total_demo_updates'] + merged['total_bio_updates']) / (merged['total_activity'] + 1)
    
    # Composite Sentiment Index (0-100)
    merged['sentiment_index'] = (
        merged['stability_score'] * 30 +
        merged['growth_score'] * 100 * 35 +
        merged['engagement_score'] * 100 * 35
    ).clip(0, 100)
    
    # Classification
    def classify_sentiment(score):
        if score >= 70: return 'THRIVING'
        elif score >= 50: return 'STABLE'
        elif score >= 30: return 'STRUGGLING'
        else: return 'AT_RISK'
    
    merged['sentiment_category'] = merged['sentiment_index'].apply(classify_sentiment)
    
    return merged


# =============================================================================
# MODULE 08: COHORT TRACKING
# =============================================================================

def track_cohort_progression(enrol_df, demo_df, bio_df):
    """
    Track age cohorts as they progress through the system.
    Detect: Children enrolled at 0-5 who never appear in 5-17 updates
    """
    # Get totals by age group
    enrol_cohorts = {
        'age_0_5_enrolled': enrol_df['age_0_5'].sum(),
        'age_5_17_enrolled': enrol_df['age_5_17'].sum(),
        'age_18_plus_enrolled': enrol_df['age_18_greater'].sum()
    }
    
    demo_cohorts = {
        'age_5_17_demo_updated': demo_df['demo_age_5_17'].sum(),
        'age_17_plus_demo_updated': demo_df['demo_age_17_'].sum()
    }
    
    bio_cohorts = {
        'age_5_17_bio_updated': bio_df['bio_age_5_17'].sum(),
        'age_17_plus_bio_updated': bio_df['bio_age_17_'].sum()
    }
    
    # Calculate survival rates (simplified)
    survival_0_5_to_5_17 = min(1.0, demo_cohorts['age_5_17_demo_updated'] / (enrol_cohorts['age_0_5_enrolled'] + 1))
    survival_5_17_to_adult = min(1.0, demo_cohorts['age_17_plus_demo_updated'] / (enrol_cohorts['age_5_17_enrolled'] + 1))
    
    return {
        'enrolled': enrol_cohorts,
        'demo_updated': demo_cohorts,
        'bio_updated': bio_cohorts,
        'survival_rate_0_5_to_5_17': survival_0_5_to_5_17,
        'survival_rate_5_17_to_adult': survival_5_17_to_adult,
        'at_risk_children': enrol_cohorts['age_0_5_enrolled'] * (1 - survival_0_5_to_5_17)
    }


def get_district_cohort_survival(enrol_df, demo_df, level='district'):
    """Calculate cohort survival rates by district."""
    group_cols = ['state'] if level == 'state' else ['state', 'district']
    
    enrol_agg = enrol_df.groupby(group_cols).agg({
        'age_0_5': 'sum', 'age_5_17': 'sum'
    }).reset_index()
    
    demo_agg = demo_df.groupby(group_cols).agg({
        'demo_age_5_17': 'sum', 'demo_age_17_': 'sum'
    }).reset_index()
    
    merged = enrol_agg.merge(demo_agg, on=group_cols, how='outer').fillna(0)
    
    merged['survival_rate'] = np.where(
        merged['age_0_5'] > 0,
        np.minimum(1.0, merged['demo_age_5_17'] / merged['age_0_5']),
        0
    )
    
    merged['at_risk_count'] = merged['age_0_5'] * (1 - merged['survival_rate'])
    
    return merged


# =============================================================================
# MODULE 09: POLICY IMPACT ANALYSIS
# =============================================================================

def analyze_policy_periods(enrol_df, demo_df, bio_df, policy_dates=None):
    """
    Analyze Aadhaar patterns around known policy events.
    Default policy dates: Demonetization (Nov 2016), COVID (Mar 2020)
    """
    if policy_dates is None:
        policy_dates = {
            'demonetization': '2016-11-08',
            'covid_lockdown': '2020-03-24',
            'digital_india': '2015-07-01'
        }
    
    # Daily totals
    enrol_daily = enrol_df.groupby('date')['total_enrolments'].sum().reset_index()
    enrol_daily.columns = ['date', 'enrolments']
    
    results = {}
    for policy_name, policy_date in policy_dates.items():
        policy_dt = pd.to_datetime(policy_date)
        
        # Get 30 days before and after
        before = enrol_daily[(enrol_daily['date'] >= policy_dt - timedelta(days=30)) & 
                             (enrol_daily['date'] < policy_dt)]
        after = enrol_daily[(enrol_daily['date'] >= policy_dt) & 
                            (enrol_daily['date'] < policy_dt + timedelta(days=30))]
        
        if len(before) > 0 and len(after) > 0:
            before_avg = before['enrolments'].mean()
            after_avg = after['enrolments'].mean()
            change_pct = ((after_avg - before_avg) / (before_avg + 1)) * 100
            
            results[policy_name] = {
                'before_avg': before_avg,
                'after_avg': after_avg,
                'change_percent': change_pct,
                'impact': 'POSITIVE' if change_pct > 10 else ('NEGATIVE' if change_pct < -10 else 'NEUTRAL')
            }
    
    return results


# =============================================================================
# MODULE 10: ECONOMIC CALENDAR PATTERNS
# =============================================================================

def detect_seasonal_patterns(enrol_df, demo_df, bio_df):
    """
    Detect seasonal patterns in Aadhaar activity.
    - Harvest migration waves
    - Festival patterns
    - Educational calendar effects
    """
    # Monthly aggregation
    enrol_df['month_name'] = enrol_df['date'].dt.month_name()
    monthly = enrol_df.groupby('month').agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum'
    }).reset_index()
    
    # Weekday patterns
    enrol_df['weekday_name'] = enrol_df['date'].dt.day_name()
    weekday = enrol_df.groupby('weekday').agg({
        'total_enrolments': 'sum'
    }).reset_index()
    
    # Find peak and trough
    peak_month = monthly.loc[monthly['total_enrolments'].idxmax()]
    trough_month = monthly.loc[monthly['total_enrolments'].idxmin()]
    
    return {
        'monthly_pattern': monthly.to_dict('records'),
        'weekday_pattern': weekday.to_dict('records'),
        'peak_month': int(peak_month['month']),
        'trough_month': int(trough_month['month']),
        'seasonality_strength': (peak_month['total_enrolments'] - trough_month['total_enrolments']) / (monthly['total_enrolments'].mean() + 1)
    }


# =============================================================================
# MODULE 11: FUTURE DEMAND EQUATION
# =============================================================================

def calculate_future_demand(enrol_df, demo_df, bio_df, years_ahead=10):
    """
    The Future Demand Equation:
    Future_Need = f(current_enrolments, update_velocity, cohort_survival, growth_rate)
    """
    # Current state
    total_enrol = enrol_df['total_enrolments'].sum()
    total_0_5 = enrol_df['age_0_5'].sum()
    total_5_17 = enrol_df['age_5_17'].sum()
    total_adult = enrol_df['age_18_greater'].sum()
    
    # Growth estimation
    yearly = enrol_df.groupby('year')['total_enrolments'].sum()
    if len(yearly) > 1:
        growth_rate = yearly.pct_change().mean()
    else:
        growth_rate = 0.02  # Default 2%
    
    growth_rate = np.clip(growth_rate, -0.1, 0.2)  # Reasonable bounds
    
    # Cohort tracking
    cohort_data = track_cohort_progression(enrol_df, demo_df, bio_df)
    
    # Generate forecasts
    forecasts = []
    for year in range(1, years_ahead + 1):
        growth_factor = (1 + growth_rate) ** year
        
        forecasts.append({
            'year_ahead': year,
            'projected_total_enrolments': total_enrol * growth_factor,
            'projected_school_children': total_0_5 * growth_factor * cohort_data['survival_rate_0_5_to_5_17'],
            'projected_working_age': total_5_17 * growth_factor * cohort_data['survival_rate_5_17_to_adult'],
            'school_seats_needed': total_0_5 * growth_factor * 0.8,
            'healthcare_visits_needed': total_enrol * growth_factor * 2,
            'pension_beneficiaries': total_adult * growth_factor * 0.15 * (1 + year * 0.01)
        })
    
    return pd.DataFrame(forecasts)


# =============================================================================
# MASTER SUMMARY FUNCTION
# =============================================================================

def generate_full_analysis_summary(enrol_df, demo_df, bio_df):
    """Generate comprehensive summary of all 11 modules."""
    
    print("🔄 Running all 11 analysis modules...")
    
    summary = {
        'life_event_velocity': calculate_life_event_velocity(enrol_df, demo_df, bio_df, 'state').describe().to_dict(),
        'crisis_signals': get_crisis_summary(enrol_df, demo_df, bio_df),
        'sentiment_index': calculate_sentiment_index(enrol_df, demo_df, bio_df, 'state')[['state', 'sentiment_index', 'sentiment_category']].head(10).to_dict('records'),
        'cohort_tracking': track_cohort_progression(enrol_df, demo_df, bio_df),
        'seasonal_patterns': detect_seasonal_patterns(enrol_df, demo_df, bio_df),
        'future_demand': calculate_future_demand(enrol_df, demo_df, bio_df, 5).to_dict('records')
    }
    
    print("✅ All modules completed!")
    return summary
