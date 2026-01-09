"""
AADHAAR PULSE - Module 03: Predictive Service Demand Forecaster
================================================================
Forecast future demand for government services based on current
enrollment patterns and demographic trends.

Key Insight: 0-5 enrolments today → School capacity needed in 5-13 years
            5-17 demographic updates → Current education/healthcare pressure

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


def forecast_school_demand(enrol_df, years_ahead=5):
    """
    Forecast school seat demand based on 0-5 age enrolments.
    
    Logic: Children enrolled at age 0-5 will need school seats in 5-13 years.
    """
    
    # Aggregate by state and year
    state_yearly = enrol_df.groupby(['state', 'year']).agg({
        'age_0_5': 'sum',
        'age_5_17': 'sum'
    }).reset_index()
    
    # Calculate growth rate
    state_yearly['age_0_5_growth'] = state_yearly.groupby('state')['age_0_5'].pct_change()
    
    # Get latest data per state
    latest_year = state_yearly['year'].max()
    latest_data = state_yearly[state_yearly['year'] == latest_year].copy()
    
    # Simple linear projection
    forecasts = []
    for _, row in latest_data.iterrows():
        state = row['state']
        current_0_5 = row['age_0_5']
        growth_rate = state_yearly[state_yearly['state'] == state]['age_0_5_growth'].mean()
        growth_rate = 0.02 if pd.isna(growth_rate) else growth_rate  # Default 2% growth
        
        for year_offset in range(1, years_ahead + 1):
            projected_students = current_0_5 * ((1 + growth_rate) ** year_offset)
            forecasts.append({
                'state': state,
                'forecast_year': latest_year + year_offset,
                'projected_school_age_children': projected_students,
                'primary_school_seats_needed': projected_students * 0.7,  # 70% will need primary
                'secondary_school_seats_needed': projected_students * 0.5,  # 50% secondary
                'growth_rate_used': growth_rate
            })
    
    return pd.DataFrame(forecasts)


def forecast_healthcare_demand(enrol_df, bio_df, years_ahead=5):
    """
    Forecast healthcare infrastructure needs based on biometric updates
    and age distribution.
    
    Logic: Biometric updates often correlate with healthcare visits.
    """
    
    # Aggregate by state
    enrol_state = enrol_df.groupby('state').agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_18_greater': 'sum'
    }).reset_index()
    
    bio_state = bio_df.groupby('state').agg({
        'total_bio_updates': 'sum'
    }).reset_index()
    
    merged = enrol_state.merge(bio_state, on='state', how='outer').fillna(0)
    
    # Healthcare demand indicators
    merged['child_healthcare_pressure'] = merged['age_0_5'] * 3  # Children need 3x visits
    merged['adult_healthcare_pressure'] = merged['age_18_greater'] * 1.5
    merged['biometric_healthcare_correlation'] = merged['total_bio_updates'] * 0.1
    
    merged['total_healthcare_demand'] = (
        merged['child_healthcare_pressure'] +
        merged['adult_healthcare_pressure'] +
        merged['biometric_healthcare_correlation']
    )
    
    # Estimate beds needed (simplified)
    merged['hospital_beds_needed'] = merged['total_healthcare_demand'] / 1000
    merged['primary_health_centers_needed'] = merged['total_healthcare_demand'] / 5000
    
    return merged


def forecast_pension_beneficiaries(enrol_df, demo_df, years_ahead=10):
    """
    Forecast pension/social security beneficiaries.
    
    Logic: Track 18+ enrolments and demographic updates to estimate
    future elderly population needing social services.
    """
    
    # Aggregate by state
    enrol_state = enrol_df.groupby(['state', 'year']).agg({
        'age_18_greater': 'sum'
    }).reset_index()
    
    # Calculate aging rate (simplified)
    latest_year = enrol_state['year'].max()
    
    forecasts = []
    for state in enrol_state['state'].unique():
        state_data = enrol_state[enrol_state['state'] == state]
        current_adult = state_data[state_data['year'] == latest_year]['age_18_greater'].sum()
        
        # Estimate: 15% of adult enrolments will be pension-age in 10 years
        pension_rate = 0.15
        
        for year_offset in range(1, years_ahead + 1):
            # Progressive aging
            projected_pensioners = current_adult * (pension_rate + (year_offset * 0.01))
            forecasts.append({
                'state': state,
                'forecast_year': latest_year + year_offset,
                'projected_pension_beneficiaries': projected_pensioners,
                'monthly_pension_budget_cr': projected_pensioners * 1000 / 1e7  # ₹1000/month
            })
    
    return pd.DataFrame(forecasts)


def calculate_infrastructure_gap(enrol_df, demo_df, bio_df):
    """
    Calculate current infrastructure gap by comparing demand vs capacity.
    """
    
    school_forecast = forecast_school_demand(enrol_df, years_ahead=1)
    healthcare_forecast = forecast_healthcare_demand(enrol_df, bio_df)
    
    # Merge forecasts
    gap_analysis = school_forecast.groupby('state').agg({
        'primary_school_seats_needed': 'sum',
        'secondary_school_seats_needed': 'sum'
    }).reset_index()
    
    gap_analysis = gap_analysis.merge(
        healthcare_forecast[['state', 'hospital_beds_needed', 'primary_health_centers_needed']],
        on='state', how='outer'
    )
    
    # Rank states by infrastructure need
    gap_analysis['infrastructure_priority_score'] = (
        gap_analysis['primary_school_seats_needed'] / gap_analysis['primary_school_seats_needed'].max() * 25 +
        gap_analysis['secondary_school_seats_needed'] / gap_analysis['secondary_school_seats_needed'].max() * 25 +
        gap_analysis['hospital_beds_needed'] / gap_analysis['hospital_beds_needed'].max() * 25 +
        gap_analysis['primary_health_centers_needed'] / gap_analysis['primary_health_centers_needed'].max() * 25
    )
    
    return gap_analysis.sort_values('infrastructure_priority_score', ascending=False)


def generate_demand_forecast_summary(enrol_df, demo_df, bio_df):
    """
    Generate comprehensive demand forecast summary.
    """
    
    school_5yr = forecast_school_demand(enrol_df, years_ahead=5)
    healthcare = forecast_healthcare_demand(enrol_df, bio_df)
    pension_10yr = forecast_pension_beneficiaries(enrol_df, demo_df, years_ahead=10)
    infrastructure_gap = calculate_infrastructure_gap(enrol_df, demo_df, bio_df)
    
    summary = {
        # School demand
        'total_school_seats_needed_5yr': school_5yr['primary_school_seats_needed'].sum(),
        'top_school_demand_states': school_5yr.groupby('state')['primary_school_seats_needed'].sum().nlargest(5).to_dict(),
        
        # Healthcare demand
        'total_hospital_beds_needed': healthcare['hospital_beds_needed'].sum(),
        'total_phc_needed': healthcare['primary_health_centers_needed'].sum(),
        'top_healthcare_demand_states': healthcare.nlargest(5, 'total_healthcare_demand')[['state', 'total_healthcare_demand']].to_dict('records'),
        
        # Pension forecast
        'total_pension_beneficiaries_10yr': pension_10yr[pension_10yr['forecast_year'] == pension_10yr['forecast_year'].max()]['projected_pension_beneficiaries'].sum(),
        'total_pension_budget_cr_10yr': pension_10yr[pension_10yr['forecast_year'] == pension_10yr['forecast_year'].max()]['monthly_pension_budget_cr'].sum() * 12,
        
        # Infrastructure priority
        'top_priority_states': infrastructure_gap.head(5)[['state', 'infrastructure_priority_score']].to_dict('records')
    }
    
    return summary


def print_demand_forecast_report(summary):
    """
    Print formatted demand forecast report.
    """
    print("\n" + "="*60)
    print("📊 PREDICTIVE SERVICE DEMAND FORECAST")
    print("="*60)
    
    print(f"\n🏫 EDUCATION (5-Year Forecast)")
    print(f"   Total School Seats Needed: {summary['total_school_seats_needed_5yr']:,.0f}")
    print(f"\n   Top States by School Demand:")
    for state, seats in summary['top_school_demand_states'].items():
        print(f"   • {state}: {seats:,.0f} seats")
    
    print(f"\n🏥 HEALTHCARE")
    print(f"   Hospital Beds Needed: {summary['total_hospital_beds_needed']:,.0f}")
    print(f"   Primary Health Centers Needed: {summary['total_phc_needed']:,.0f}")
    
    print(f"\n👴 PENSION (10-Year Forecast)")
    print(f"   Projected Beneficiaries: {summary['total_pension_beneficiaries_10yr']:,.0f}")
    print(f"   Annual Budget Required: ₹{summary['total_pension_budget_cr_10yr']:,.0f} Crore")
    
    print(f"\n🎯 INFRASTRUCTURE PRIORITY STATES")
    for item in summary['top_priority_states']:
        print(f"   • {item['state']}: Score {item['infrastructure_priority_score']:.1f}")
    
    print("\n" + "="*60)
