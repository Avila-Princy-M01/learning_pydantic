import sys
import os
import pandas as pd

# Add the 3_CODE directory to sys.path to handle the numeric folder name
code_dir = os.path.join(os.getcwd(), 'aadhaar_pulse', '3_CODE')
if code_dir not in sys.path:
    sys.path.append(code_dir)

try:
    import data_loader
    import preprocessing
    import module_01_migration
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Code directory: {code_dir}")
    sys.exit(1)

def main():
    print("Starting Aadhaar Data Analysis...")
    print("="*60)
    
    # 1. Load Data
    try:
        enrol, demo, bio = data_loader.load_all_datasets()
    except Exception as e:
        print(f"Failed to load data: {e}")
        return

    # 2. Preprocess
    print("\nPreprocessing Data...")
    try:
        enrol_clean, demo_clean, bio_clean = preprocessing.clean_all_datasets(enrol, demo, bio)
    except Exception as e:
        print(f"Failed to preprocess data: {e}")
        return

    # 3. Run Module 1 Analysis (Migration)
    print("\nRunning Migration Analysis (Module 01)...")
    try:
        migration_summary = module_01_migration.generate_migration_summary(enrol_clean, demo_clean)
        module_01_migration.print_migration_report(migration_summary)
    except Exception as e:
        print(f"Failed to run migration analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
