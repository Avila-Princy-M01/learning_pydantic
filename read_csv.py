import pandas as pd

# Read first few rows of each dataset
print("=== ENROLMENT DATA ===")
df_enrol = pd.read_csv('api_data_aadhar_enrolment/api_data_aadhar_enrolment_0_500000.csv', nrows=5)
print(df_enrol.columns.tolist())
print(df_enrol.head())

print("\n=== DEMOGRAPHIC DATA ===")
df_demo = pd.read_csv('api_data_aadhar_demographic/api_data_aadhar_demographic_0_500000.csv', nrows=5)
print(df_demo.columns.tolist())
print(df_demo.head())

print("\n=== BIOMETRIC DATA ===")
df_bio = pd.read_csv('api_data_aadhar_biometric/api_data_aadhar_biometric_0_500000.csv', nrows=5)
print(df_bio.columns.tolist())
print(df_bio.head())
