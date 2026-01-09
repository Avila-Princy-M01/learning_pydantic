import os
import glob
from pathlib import Path

data_path = Path('api_data_aadhar_enrolment')
print(f"Path: {data_path}")
all_files = glob.glob(str(data_path / '*.csv'))
print(f"Files found: {len(all_files)}")
for f in all_files:
    print(f)
