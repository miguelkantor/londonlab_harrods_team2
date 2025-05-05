# -*- coding: utf-8 -*-
"""
Created on Tue Apr 29 10:11:20 2025

@author: mkant
"""
import zipfile
import pandas as pd
import io
import os

def get_date_range_from_csv(file_like):
    """Read only the FLIGHT_LEG_ARRIVAL_DATE column and find min and max."""
    min_date = None
    max_date = None
    
    for chunk in pd.read_csv(file_like, usecols=['FLIGHT_LEG_ARRIVAL_DATE'], parse_dates=['FLIGHT_LEG_ARRIVAL_DATE'], chunksize=100000):
        chunk_min = chunk['FLIGHT_LEG_ARRIVAL_DATE'].min()
        chunk_max = chunk['FLIGHT_LEG_ARRIVAL_DATE'].max()
        
        if (min_date is None) or (chunk_min < min_date):
            min_date = chunk_min
        if (max_date is None) or (chunk_max > max_date):
            max_date = chunk_max
    
    return min_date, max_date

def list_csvs_in_zip(zip_bytes, parent_path=''):
    """Recursively find all CSV files inside ZIPs and get date ranges."""
    records = []

    with zipfile.ZipFile(zip_bytes) as z:
        for name in z.namelist():
            full_path = os.path.join(parent_path, name)
            if name.endswith('.csv'):
                with z.open(name) as f:
                    # Need to wrap the file handle in BytesIO for pandas to seek properly
                    f_bytes = io.BytesIO(f.read())
                    earliest, latest = get_date_range_from_csv(f_bytes)
                records.append({
                    'csv_file_path': full_path,
                    'earliest_date': earliest,
                    'latest_date': latest
                })
                print(f"Processed: {full_path} | Earliest: {earliest.date()} | Latest: {latest.date()}")

            elif name.endswith('.zip'):
                with z.open(name) as nested_zip:
                    nested_bytes = io.BytesIO(nested_zip.read())
                    records.extend(list_csvs_in_zip(nested_bytes, parent_path=full_path))
    
    return records

# ---- Main execution ----

# Change working directory
os.chdir(r'C:\Users\mkant\Documents\Intro to Python\Code')

# Path to your main zip
zip_path = 'LBS.zip'

# Start processing
with open(zip_path, 'rb') as f:
    top_zip_bytes = io.BytesIO(f.read())

csv_records = list_csvs_in_zip(top_zip_bytes)
csv_paths = [rec['csv_file_path'] for rec in csv_records]   # <-- add this line

# Build DataFrame
df = pd.DataFrame(csv_records)

# Show result
print(df)

# %%
import zipfile
import pandas as pd
import io

# %%
# Open the top-level zip
# %% -------- CONFIG --------
import zipfile, io, pandas as pd, os
csv_paths = [rec['csv_file_path'] for rec in csv_records]   # <-- add this line

zip_path   = r'LBS.zip'

usecols = [
    'FLIGHT_LEG_ARRIVAL_DATE',
    'TRIP_ORIGIN_COUNTRY',
    'TRIP_ORIGIN_REGION',
    'LOS_AT_DESTINATION_CAT',
    'LOS_AT_DESTINATION_NIGHTS',
    'PAX_PROFILE',
    'PAX_NATIONALITY',
    'PAX'
]

agg_cols = [
    'FLIGHT_LEG_ARRIVAL_DATE',
    'TRIP_ORIGIN_COUNTRY',
    'TRIP_ORIGIN_REGION',
    'LOS_AT_DESTINATION_CAT',
    'LOS_AT_DESTINATION_NIGHTS',
    'PAX_NATIONALITY',
    'PAX_PROFILE'
]


dfs = []  # collect grouped chunks here

# %% -------- PROCESS EACH CSV --------
with zipfile.ZipFile(zip_path) as z_top:
    for path in csv_paths:
        nested_zip_name, inner_csv_name = path.split('\\', 1)    # split “zip\csv”
        with z_top.open(nested_zip_name) as nz_bytes:
            with zipfile.ZipFile(io.BytesIO(nz_bytes.read())) as nz:
                with nz.open(inner_csv_name) as csv_file:
                    df = pd.read_csv(csv_file, usecols=usecols)

        # separate positive/negative pax
        df['positive_pax'] = df['PAX'].clip(lower=0)
        df['negative_pax'] = (-df['PAX']).clip(lower=0)

        grouped = (
            df.groupby(agg_cols, dropna=False)
              .agg(sum_positive_pax=('positive_pax', 'sum'),
                   sum_negative_pax=('negative_pax', 'sum'),
                   flight_count     =('PAX',           'count'))
              .reset_index()
        )
        
        # ----- diagnostics: country-loss check -----
        raw_set     = set(df['TRIP_ORIGIN_COUNTRY'].dropna().astype(str))
        grouped_set = set(grouped['TRIP_ORIGIN_COUNTRY'].dropna().astype(str))
        lost        = sorted(raw_set - grouped_set)
        
        print(
            f"{inner_csv_name}: {len(raw_set)} → {len(grouped_set)} countries; "
            f"lost {len(lost)}: {lost[:10]}{' …' if len(lost) > 10 else ''}"
        )
        # ------------------------------------------

        dfs.append(grouped)
        print(f'✔ processed {inner_csv_name}')

# %% -------- BUILD MASTER & SAVE --------
master = pd.concat(dfs, ignore_index=True)
# final collapse in case the same date-origin-LOS combo occurs in >1 file
master = (
    master.groupby(agg_cols, dropna = False, as_index=False)
          .agg(sum_positive_pax=('sum_positive_pax', 'sum'),
               sum_negative_pax=('sum_negative_pax', 'sum'),
               flight_count    =('flight_count',     'sum'))
)

out_path = r'C:/Users/mkant/Documents/Intro to Python/CODE/LondonLab Data/flights_grouped_master.csv'
master.to_csv(out_path, index=False)
print(f'✅ master saved to {out_path}')
# %% -------- OPEN MASTER & EXPLORE --------
import pandas as pd

# Load the saved master CSV
master_path = r'C:/Users/mkant/Documents/Intro to Python/CODE/LondonLab Data/flights_grouped_master.csv'
df = pd.read_csv(master_path)

# Parse the date column properly
df['FLIGHT_LEG_ARRIVAL_DATE'] = pd.to_datetime(df['FLIGHT_LEG_ARRIVAL_DATE'])

# Print number of rows
print(f"✅ Number of rows: {len(df)}")

# Print count of unique values for each column
print("\n✅ Unique values per column:")
print(df.nunique())

# Print the first and last date
print("\n✅ Date range:")
print(f"First date: {df['FLIGHT_LEG_ARRIVAL_DATE'].min().date()}")
print(f"Last date:  {df['FLIGHT_LEG_ARRIVAL_DATE'].max().date()}")

# Print the head
print("\n✅ Data preview:")
print(df.head())

# %% RE-GROUP TO REMOVE LOS COLUMNS
agg_cols = [
    'FLIGHT_LEG_ARRIVAL_DATE',
    'TRIP_ORIGIN_COUNTRY',
    'TRIP_ORIGIN_REGION',
    'PAX_NATIONALITY',
    'PAX_PROFILE'
]

df_reduced = (
    df.groupby(agg_cols, as_index=False)
      .agg(
          sum_positive_pax=('sum_positive_pax', 'sum'),
          sum_negative_pax=('sum_negative_pax', 'sum'),
          flight_count=('flight_count', 'sum')
      )
)

print("✅ Reduced DataFrame shape:", df_reduced.shape)
print(df_reduced.head())

# %% SAVE REDUCED DATA WITHOUT LOS
output_path = r'C:/Users/mkant/Documents/Intro to Python/CODE/flights_grouped_master_without_los.csv'
df_reduced.to_csv(output_path, index=False)
print(f"✅ Saved reduced data to: {output_path}")

