"""
AADHAAR PULSE - Data Preprocessing Module
==========================================
Functions to clean, transform, and merge Aadhaar datasets.

Author: Aadhaar Pulse Team
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


def clean_enrolment_data(df):
    """
    Clean the enrolment dataset.
    
    Steps:
    1. Remove duplicates
    2. Handle missing values
    3. Standardize column names
    4. Add derived columns
    """
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Fill missing numeric values with 0
    numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # Calculate total enrolments
    df['total_enrolments'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
    
    # Extract date components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.dayofweek
    df['week'] = df['date'].dt.isocalendar().week
    
    # Standardize state names (uppercase)
    df['state'] = df['state'].str.upper().str.strip()
    df['district'] = df['district'].str.upper().str.strip()
    
    return df


def clean_demographic_data(df):
    """
    Clean the demographic update dataset.
    """
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Fill missing numeric values with 0
    numeric_cols = ['demo_age_5_17', 'demo_age_17_']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # Calculate total demographic updates
    df['total_demo_updates'] = df['demo_age_5_17'] + df['demo_age_17_']
    
    # Extract date components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.dayofweek
    df['week'] = df['date'].dt.isocalendar().week
    
    # Standardize names
    df['state'] = df['state'].str.upper().str.strip()
    df['district'] = df['district'].str.upper().str.strip()
    
    return df


def clean_biometric_data(df):
    """
    Clean the biometric update dataset.
    """
    df = df.copy()
    
    # Remove duplicates
    df = df.drop_duplicates()
    
    # Fill missing numeric values with 0
    numeric_cols = ['bio_age_5_17', 'bio_age_17_']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype(int)
    
    # Calculate total biometric updates
    df['total_bio_updates'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    # Extract date components
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.dayofweek
    df['week'] = df['date'].dt.isocalendar().week
    
    # Standardize names
    df['state'] = df['state'].str.upper().str.strip()
    df['district'] = df['district'].str.upper().str.strip()
    
    return df


def clean_all_datasets(enrol_df, demo_df, bio_df):
    """
    Clean all three datasets.
    
    Returns:
    --------
    tuple
        (cleaned_enrolment, cleaned_demographic, cleaned_biometric)
    """
    print("🧹 Cleaning Enrolment Data...")
    enrol_clean = clean_enrolment_data(enrol_df)
    print(f"   ✓ Cleaned {len(enrol_clean):,} records")
    
    print("🧹 Cleaning Demographic Data...")
    demo_clean = clean_demographic_data(demo_df)
    print(f"   ✓ Cleaned {len(demo_clean):,} records")
    
    print("🧹 Cleaning Biometric Data...")
    bio_clean = clean_biometric_data(bio_df)
    print(f"   ✓ Cleaned {len(bio_clean):,} records")
    
    print("\n✅ All datasets cleaned!")
    
    return enrol_clean, demo_clean, bio_clean


def aggregate_by_state(df, value_cols, date_col='date'):
    """
    Aggregate data by state and date.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input dataframe
    value_cols : list
        List of columns to sum
    date_col : str
        Date column name
    
    Returns:
    --------
    pd.DataFrame
        Aggregated dataframe
    """
    agg_dict = {col: 'sum' for col in value_cols}
    return df.groupby(['state', date_col]).agg(agg_dict).reset_index()


def aggregate_by_district(df, value_cols, date_col='date'):
    """
    Aggregate data by state, district and date.
    """
    agg_dict = {col: 'sum' for col in value_cols}
    return df.groupby(['state', 'district', date_col]).agg(agg_dict).reset_index()


def aggregate_by_pincode(df, value_cols, date_col='date'):
    """
    Aggregate data by pincode and date.
    """
    agg_dict = {col: 'sum' for col in value_cols}
    return df.groupby(['state', 'district', 'pincode', date_col]).agg(agg_dict).reset_index()


def merge_all_datasets(enrol_df, demo_df, bio_df, level='district'):
    """
    Merge all three datasets at specified aggregation level.
    
    Parameters:
    -----------
    enrol_df : pd.DataFrame
        Enrolment data
    demo_df : pd.DataFrame
        Demographic update data
    bio_df : pd.DataFrame
        Biometric update data
    level : str
        Aggregation level: 'state', 'district', or 'pincode'
    
    Returns:
    --------
    pd.DataFrame
        Merged dataset with all metrics
    """
    
    if level == 'state':
        # Aggregate enrolment
        enrol_agg = enrol_df.groupby(['state', 'year', 'month']).agg({
            'age_0_5': 'sum',
            'age_5_17': 'sum', 
            'age_18_greater': 'sum',
            'total_enrolments': 'sum'
        }).reset_index()
        
        # Aggregate demographic
        demo_agg = demo_df.groupby(['state', 'year', 'month']).agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum',
            'total_demo_updates': 'sum'
        }).reset_index()
        
        # Aggregate biometric
        bio_agg = bio_df.groupby(['state', 'year', 'month']).agg({
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'total_bio_updates': 'sum'
        }).reset_index()
        
        # Merge
        merged = enrol_agg.merge(demo_agg, on=['state', 'year', 'month'], how='outer')
        merged = merged.merge(bio_agg, on=['state', 'year', 'month'], how='outer')
        
    elif level == 'district':
        # Aggregate enrolment
        enrol_agg = enrol_df.groupby(['state', 'district', 'year', 'month']).agg({
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum',
            'total_enrolments': 'sum'
        }).reset_index()
        
        # Aggregate demographic
        demo_agg = demo_df.groupby(['state', 'district', 'year', 'month']).agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum',
            'total_demo_updates': 'sum'
        }).reset_index()
        
        # Aggregate biometric
        bio_agg = bio_df.groupby(['state', 'district', 'year', 'month']).agg({
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'total_bio_updates': 'sum'
        }).reset_index()
        
        # Merge
        merged = enrol_agg.merge(demo_agg, on=['state', 'district', 'year', 'month'], how='outer')
        merged = merged.merge(bio_agg, on=['state', 'district', 'year', 'month'], how='outer')
        
    else:  # pincode level
        # Aggregate at pincode level
        enrol_agg = enrol_df.groupby(['state', 'district', 'pincode', 'year', 'month']).agg({
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum',
            'total_enrolments': 'sum'
        }).reset_index()
        
        demo_agg = demo_df.groupby(['state', 'district', 'pincode', 'year', 'month']).agg({
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum',
            'total_demo_updates': 'sum'
        }).reset_index()
        
        bio_agg = bio_df.groupby(['state', 'district', 'pincode', 'year', 'month']).agg({
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'total_bio_updates': 'sum'
        }).reset_index()
        
        merged = enrol_agg.merge(demo_agg, on=['state', 'district', 'pincode', 'year', 'month'], how='outer')
        merged = merged.merge(bio_agg, on=['state', 'district', 'pincode', 'year', 'month'], how='outer')
    
    # Fill NaN with 0 for numeric columns
    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    # Calculate derived metrics
    merged['total_activity'] = (merged['total_enrolments'] + 
                                 merged['total_demo_updates'] + 
                                 merged['total_bio_updates'])
    
    # Update-to-Enrolment Ratio (UER) - key metric for migration detection
    merged['update_enrol_ratio'] = np.where(
        merged['total_enrolments'] > 0,
        (merged['total_demo_updates'] + merged['total_bio_updates']) / merged['total_enrolments'],
        0
    )
    
    return merged


def create_time_series(df, date_col='date', value_col='total_enrolments', freq='D'):
    """
    Create a time series from the data.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Input data
    date_col : str
        Date column name
    value_col : str
        Value column to aggregate
    freq : str
        Frequency: 'D' (daily), 'W' (weekly), 'M' (monthly)
    
    Returns:
    --------
    pd.DataFrame
        Time series data
    """
    ts = df.groupby(pd.Grouper(key=date_col, freq=freq))[value_col].sum().reset_index()
    ts.columns = ['date', 'value']
    return ts


def get_state_summary(enrol_df, demo_df, bio_df):
    """
    Get summary statistics by state.
    
    Returns:
    --------
    pd.DataFrame
        State-level summary with all metrics
    """
    # Enrolment summary
    enrol_state = enrol_df.groupby('state').agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'district': 'nunique',
        'pincode': 'nunique'
    }).reset_index()
    enrol_state.columns = ['state', 'total_enrolments', 'enrol_0_5', 'enrol_5_17', 
                           'enrol_18_plus', 'num_districts', 'num_pincodes']
    
    # Demographic summary
    demo_state = demo_df.groupby('state').agg({
        'total_demo_updates': 'sum',
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_state.columns = ['state', 'total_demo_updates', 'demo_5_17', 'demo_17_plus']
    
    # Biometric summary
    bio_state = bio_df.groupby('state').agg({
        'total_bio_updates': 'sum',
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    bio_state.columns = ['state', 'total_bio_updates', 'bio_5_17', 'bio_17_plus']
    
    # Merge all
    summary = enrol_state.merge(demo_state, on='state', how='outer')
    summary = summary.merge(bio_state, on='state', how='outer')
    
    # Fill NaN
    summary = summary.fillna(0)
    
    # Calculate total activity
    summary['total_activity'] = (summary['total_enrolments'] + 
                                  summary['total_demo_updates'] + 
                                  summary['total_bio_updates'])
    
    # Calculate ratios
    summary['update_enrol_ratio'] = np.where(
        summary['total_enrolments'] > 0,
        (summary['total_demo_updates'] + summary['total_bio_updates']) / summary['total_enrolments'],
        0
    )
    
    return summary.sort_values('total_activity', ascending=False)


def get_district_summary(enrol_df, demo_df, bio_df):
    """
    Get summary statistics by district.
    
    Returns:
    --------
    pd.DataFrame
        District-level summary with all metrics
    """
    # Enrolment summary
    enrol_dist = enrol_df.groupby(['state', 'district']).agg({
        'total_enrolments': 'sum',
        'age_0_5': 'sum',
        'age_5_17': 'sum',
        'age_18_greater': 'sum',
        'pincode': 'nunique'
    }).reset_index()
    enrol_dist.columns = ['state', 'district', 'total_enrolments', 'enrol_0_5', 
                          'enrol_5_17', 'enrol_18_plus', 'num_pincodes']
    
    # Demographic summary
    demo_dist = demo_df.groupby(['state', 'district']).agg({
        'total_demo_updates': 'sum',
        'demo_age_5_17': 'sum',
        'demo_age_17_': 'sum'
    }).reset_index()
    demo_dist.columns = ['state', 'district', 'total_demo_updates', 'demo_5_17', 'demo_17_plus']
    
    # Biometric summary
    bio_dist = bio_df.groupby(['state', 'district']).agg({
        'total_bio_updates': 'sum',
        'bio_age_5_17': 'sum',
        'bio_age_17_': 'sum'
    }).reset_index()
    bio_dist.columns = ['state', 'district', 'total_bio_updates', 'bio_5_17', 'bio_17_plus']
    
    # Merge all
    summary = enrol_dist.merge(demo_dist, on=['state', 'district'], how='outer')
    summary = summary.merge(bio_dist, on=['state', 'district'], how='outer')
    
    # Fill NaN
    summary = summary.fillna(0)
    
    # Calculate total activity
    summary['total_activity'] = (summary['total_enrolments'] + 
                                  summary['total_demo_updates'] + 
                                  summary['total_bio_updates'])
    
    # Calculate ratios
    summary['update_enrol_ratio'] = np.where(
        summary['total_enrolments'] > 0,
        (summary['total_demo_updates'] + summary['total_bio_updates']) / summary['total_enrolments'],
        0
    )
    
    # Ghost district indicator (high enrol, low updates)
    summary['ghost_score'] = np.where(
        (summary['total_enrolments'] > summary['total_enrolments'].median()) & 
        (summary['update_enrol_ratio'] < 0.1),
        1, 0
    )
    
    return summary.sort_values('total_activity', ascending=False)
