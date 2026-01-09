"""
AADHAAR PULSE - Data Loader Module
===================================
Functions to load and combine all Aadhaar datasets.

Author: Aadhaar Pulse Team
"""

import pandas as pd
import os
from pathlib import Path
import glob
import warnings
warnings.filterwarnings('ignore')


def get_project_root():
    """Get the root directory of the project."""
    return Path(__file__).parent.parent


def load_enrolment_data(data_path=None):
    """
    Load all Aadhaar enrolment CSV files and combine them.
    
    Parameters:
    -----------
    data_path : str, optional
        Path to the enrolment data folder. If None, uses default location.
    
    Returns:
    --------
    pd.DataFrame
        Combined enrolment data with columns:
        - date: Date of enrolment
        - state: State name
        - district: District name
        - pincode: PIN code
        - age_0_5: Enrolments for age 0-5
        - age_5_17: Enrolments for age 5-17
        - age_18_greater: Enrolments for age 18+
    """
    if data_path is None:
        # Try multiple possible locations
        possible_paths = [
            get_project_root() / '1_DATA' / 'enrolment',
            Path('..') / 'api_data_aadhar_enrolment',
            Path('api_data_aadhar_enrolment'),
        ]
        for p in possible_paths:
            if p.exists():
                data_path = p
                break
    
    if data_path is None:
        raise FileNotFoundError("Could not find enrolment data folder")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_path}")
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'])
    
    return combined


def load_demographic_data(data_path=None):
    """
    Load all Aadhaar demographic update CSV files and combine them.
    
    Parameters:
    -----------
    data_path : str, optional
        Path to the demographic data folder. If None, uses default location.
    
    Returns:
    --------
    pd.DataFrame
        Combined demographic update data with columns:
        - date: Date of update
        - state: State name
        - district: District name
        - pincode: PIN code
        - demo_age_5_17: Demographic updates for age 5-17
        - demo_age_17_: Demographic updates for age 17+
    """
    if data_path is None:
        possible_paths = [
            get_project_root() / '1_DATA' / 'demographic',
            Path('..') / 'api_data_aadhar_demographic',
            Path('api_data_aadhar_demographic'),
        ]
        for p in possible_paths:
            if p.exists():
                data_path = p
                break
    
    if data_path is None:
        raise FileNotFoundError("Could not find demographic data folder")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_path}")
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'])
    
    return combined


def load_biometric_data(data_path=None):
    """
    Load all Aadhaar biometric update CSV files and combine them.
    
    Parameters:
    -----------
    data_path : str, optional
        Path to the biometric data folder. If None, uses default location.
    
    Returns:
    --------
    pd.DataFrame
        Combined biometric update data with columns:
        - date: Date of update
        - state: State name
        - district: District name
        - pincode: PIN code
        - bio_age_5_17: Biometric updates for age 5-17
        - bio_age_17_: Biometric updates for age 17+
    """
    if data_path is None:
        possible_paths = [
            get_project_root() / '1_DATA' / 'biometric',
            Path('..') / 'api_data_aadhar_biometric',
            Path('api_data_aadhar_biometric'),
        ]
        for p in possible_paths:
            if p.exists():
                data_path = p
                break
    
    if data_path is None:
        raise FileNotFoundError("Could not find biometric data folder")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    if not all_files:
        raise FileNotFoundError(f"No CSV files found in {data_path}")
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'])
    
    return combined


def load_all_datasets(enrol_path=None, demo_path=None, bio_path=None):
    """
    Load all three Aadhaar datasets at once.
    
    Returns:
    --------
    tuple
        (enrolment_df, demographic_df, biometric_df)
    """
    print("📂 Loading Enrolment Data...")
    enrolment = load_enrolment_data(enrol_path)
    print(f"   ✓ Loaded {len(enrolment):,} enrolment records")
    
    print("📂 Loading Demographic Update Data...")
    demographic = load_demographic_data(demo_path)
    print(f"   ✓ Loaded {len(demographic):,} demographic records")
    
    print("📂 Loading Biometric Update Data...")
    biometric = load_biometric_data(bio_path)
    print(f"   ✓ Loaded {len(biometric):,} biometric records")
    
    print("\n✅ All datasets loaded successfully!")
    
    return enrolment, demographic, biometric


def get_data_summary(df, name="Dataset"):
    """
    Print a summary of a dataset.
    
    Parameters:
    -----------
    df : pd.DataFrame
        The dataset to summarize
    name : str
        Name of the dataset for display
    """
    print(f"\n{'='*50}")
    print(f"📊 {name} Summary")
    print(f"{'='*50}")
    print(f"Total Records: {len(df):,}")
    print(f"Date Range: {df['date'].min()} to {df['date'].max()}")
    print(f"States: {df['state'].nunique()}")
    print(f"Districts: {df['district'].nunique()}")
    print(f"Pincodes: {df['pincode'].nunique()}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nSample Data:")
    print(df.head(3).to_string())


if __name__ == "__main__":
    # Test the data loading
    try:
        enrol, demo, bio = load_all_datasets()
        get_data_summary(enrol, "Enrolment Data")
        get_data_summary(demo, "Demographic Updates")
        get_data_summary(bio, "Biometric Updates")
    except FileNotFoundError as e:
        print(f"⚠️ {e}")
        print("Please ensure data files are in the correct location.")
