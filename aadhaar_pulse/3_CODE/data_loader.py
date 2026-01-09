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


def find_data_path(subdir, alt_name):
    """
    Find the data path ensuring it contains CSV files.
    """
    possible_paths = [
        get_project_root() / '1_DATA' / subdir,
        Path('..') / alt_name,
        Path(alt_name),
        Path(os.getcwd()) / alt_name
    ]
    
    for p in possible_paths:
        if p.exists():
            files = glob.glob(str(p / '*.csv'))
            if files:
                return p
    return None

def load_enrolment_data(data_path=None):
    """
    Load all Aadhaar enrolment CSV files and combine them.
    """
    if data_path is None:
        data_path = find_data_path('enrolment', 'api_data_aadhar_enrolment')
    
    if data_path is None:
        raise FileNotFoundError("Could not find enrolment data folder with CSV files")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'], dayfirst=True)
    
    return combined


def load_demographic_data(data_path=None):
    """
    Load all Aadhaar demographic update CSV files and combine them.
    """
    if data_path is None:
        data_path = find_data_path('demographic', 'api_data_aadhar_demographic')
    
    if data_path is None:
        raise FileNotFoundError("Could not find demographic data folder with CSV files")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'], dayfirst=True)
    
    return combined


def load_biometric_data(data_path=None):
    """
    Load all Aadhaar biometric update CSV files and combine them.
    """
    if data_path is None:
        data_path = find_data_path('biometric', 'api_data_aadhar_biometric')
    
    if data_path is None:
        raise FileNotFoundError("Could not find biometric data folder with CSV files")
    
    all_files = glob.glob(str(Path(data_path) / '*.csv'))
    
    dfs = []
    for file in all_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    combined = pd.concat(dfs, ignore_index=True)
    combined['date'] = pd.to_datetime(combined['date'], dayfirst=True)
    
    return combined


def load_all_datasets(enrol_path=None, demo_path=None, bio_path=None):
    """
    Load all three Aadhaar datasets at once.
    
    Returns:
    --------
    tuple
        (enrolment_df, demographic_df, biometric_df)
    """
    print("Loading Enrolment Data...")
    enrolment = load_enrolment_data(enrol_path)
    print(f"   Loaded {len(enrolment):,} enrolment records")
    
    print("Loading Demographic Update Data...")
    demographic = load_demographic_data(demo_path)
    print(f"   Loaded {len(demographic):,} demographic records")
    
    print("Loading Biometric Update Data...")
    biometric = load_biometric_data(bio_path)
    print(f"   Loaded {len(biometric):,} biometric records")
    
    print("\nAll datasets loaded successfully!")
    
    return enrolment, demographic, biometric


def get_data_summary(df, name="Dataset"):
    """
    Print a summary of a dataset.
    """
    print(f"\n{'='*50}")
    print(f"{name} Summary")
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
