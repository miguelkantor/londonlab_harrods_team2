# -*- coding: utf-8 -*-
"""
Created on Tue May 13 16:33:33 2025

@author: mkant
"""
# %% -------- Import Flights and Group --------


import pandas as pd
import numpy as np
# Only keep the target variables for the flights data and transaction data
flights = pd.read_csv(r"C:\Users\mkant\Documents\Intro to Python\CODE\LondonLab Data\flights_grouped_master_without_los.csv")#, #changing to without LOS
#usecols = ['FLIGHT_LEG_ARRIVAL_DATE', 'TRIP_ORIGIN_COUNTRY','PAX_NATIONALITY','sum_positive_pax','sum_negative_pax'])
flights["FLIGHT_LEG_ARRIVAL_DATE"] = pd.to_datetime(
    flights["FLIGHT_LEG_ARRIVAL_DATE"], 
    errors='coerce' 
)
flights['ARRIVALS'] = flights['sum_positive_pax'] - flights['sum_negative_pax'] 
flights.drop(columns = ['sum_positive_pax','sum_negative_pax'],inplace=True)

print("Flight columns:",flights.columns)

def classify_country(code):
    # Middle East - GCC
    if code in ['AE', 'SA', 'KW', 'QA', 'OM', 'BH']:
        return 'Middle East - GCC'
    # Greater China
    elif code in ['CN', 'HK', 'TW', 'MO']:
        return 'Greater China'
    # UK
    elif code == 'GB':
        return 'UK'
    # EU (subset of Europe)
    elif code in ['AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI', 'FR', 'GR', 'HR', 'HU',
                  'IE', 'IT', 'LT', 'LU', 'LV', 'MT', 'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK']:
        return 'EU'
    # Russia separately
    elif code == 'RU':
        return 'Russia'
    # North America
    elif code in ['US', 'CA', 'MX']:
        return 'North America'
    # RO APAC (rest of Asia-Pacific including Oceania)
    elif code in ['AF', 'AM', 'AZ', 'BD', 'BN', 'BT', 'GE', 'ID', 'IL', 'IN', 'IQ', 'IR', 'JO', 'JP',
                  'KG', 'KH', 'KP', 'KR', 'KZ', 'LA', 'LB', 'LK', 'MM', 'MN', 'MV', 'MY', 'NP', 'PH',
                  'PK', 'PS', 'SG', 'SY', 'TH', 'TJ', 'TL', 'TM', 'TR', 'UZ', 'VN', 'YE', 'AS', 'AU',
                  'CK', 'FJ', 'FM', 'GU', 'KI', 'MH', 'MP', 'NC', 'NF', 'NR', 'NU', 'NZ', 'PF', 'PG',
                  'PN', 'SB', 'TK', 'TO', 'TV', 'VU', 'WS']:
        return 'RO APAC'
    else:
        return 'ROW'

flights["TRIP_ORIGIN_COUNTRY"] = flights["TRIP_ORIGIN_COUNTRY"].apply(classify_country)
flights["PAX_NATIONALITY"] = flights["PAX_NATIONALITY"].apply(classify_country)

# Aggregate number of flights by date and country
flights_grouped_daily_trip_origin = flights.groupby(["FLIGHT_LEG_ARRIVAL_DATE", "TRIP_ORIGIN_COUNTRY"])["ARRIVALS"].sum()                           .reset_index().rename(columns={'FLIGHT_LEG_ARRIVAL_DATE': 'DATE', 'TRIP_ORIGIN_COUNTRY': 'COUNTRY'})



# %% -------- Flights by Airport --------


# 1) LHR vs non-LHR arrivals
# --------------------------------
# mark each row as LHR or non_LHR
flights['dest_type'] = np.where(
    flights['FLIGHT_LEG_DESTINATION_AIRPORT'] == 'LHR',
    'LHR',
    'non_LHR'
)

# pivot to get sums
flights_airport = (
    flights
    .pivot_table(
        index=['FLIGHT_LEG_ARRIVAL_DATE', 'TRIP_ORIGIN_COUNTRY'],
        columns='dest_type',
        values='ARRIVALS',
        aggfunc='sum',
        fill_value=0
    )
    .reset_index()
    .rename(columns={'LHR': 'LHR_arrivals', 'non_LHR': 'non_LHR_arrivals'})
    .rename(columns={'FLIGHT_LEG_ARRIVAL_DATE': 'DATE', 'TRIP_ORIGIN_COUNTRY': 'COUNTRY'})
    )
# %% -------- Flights by Cabin Class --------

# 2) Cabin-class “and above” arrivals
# --------------------------------
# drop NaN cabin rows
f2 = flights[flights['TRIP_CABIN_CLASS'].notna()].copy()

# define the tiers of interest
f2['premium_economy_and_above_arrivals'] = np.where(
    f2['TRIP_CABIN_CLASS'].isin(['PREMIUM_ECONOMY', 'BUSINESS', 'FIRST']),
    f2['ARRIVALS'], 0
)
f2['business_and_above_arrivals'] = np.where(
    f2['TRIP_CABIN_CLASS'].isin(['BUSINESS', 'FIRST']),
    f2['ARRIVALS'], 0
)
f2['first_arrivals'] = np.where(
    f2['TRIP_CABIN_CLASS'] == 'FIRST',
    f2['ARRIVALS'], 0
)

flights_cabin = (
    f2
    .groupby(['FLIGHT_LEG_ARRIVAL_DATE', 'TRIP_ORIGIN_COUNTRY'], as_index=False)
    .agg(
        premium_economy_and_above_arrivals=('premium_economy_and_above_arrivals', 'sum'),
        business_and_above_arrivals        =('business_and_above_arrivals',         'sum'),
        first_arrivals                     =('first_arrivals',                      'sum')
    )
    .rename(columns={'FLIGHT_LEG_ARRIVAL_DATE': 'DATE', 'TRIP_ORIGIN_COUNTRY': 'COUNTRY'})

)

# Now you have:
# df_lhr    → columns: FLIGHT_LEG_ARRIVAL_DATE, TRIP_ORIGIN_COUNTRY, LHR_arrivals, non_LHR_arrivals
# df_cabins → columns: FLIGHT_LEG_ARRIVAL_DATE, TRIP_ORIGIN_COUNTRY, premium_economy_and_above_arrivals,
#                                               business_and_above_arrivals, first_arrivals

# %% -------- Import Transactions and Group --------
# Only keep the target variables for the flights data and transaction data
transactions = pd.read_csv(r"C:\Users\mkant\Documents\Intro to Python\CODE\LondonLab Data\RAW_LBS_TEAM1_20250428.csv",
                           usecols=['CAL_DAY','CHANNEL','CALC_COUNTRY_GP','TRANX_TTL','TIER_LATEST','ZPERSONA','MCH3'])
transactions["CAL_DAY"] = pd.to_datetime(transactions["CAL_DAY"])
transactions = transactions[transactions.CHANNEL == "Knightsbridge"]
transactions = transactions[~transactions.CALC_COUNTRY_GP.isin(['UK','Russia','ROW'])]
# flag target personas
target_list = ['VIP', 'Local Affluent', 'Jet Setter']
transactions['is_target_persona'] = transactions['ZPERSONA'].isin(target_list).astype(int)

# drop the original persona column
transactions.drop(columns=['ZPERSONA'], inplace=True)
print(transactions.head())

# Aggregate number of transactions by date and country
transactions_grouped_daily_country = transactions.groupby(["CAL_DAY","CALC_COUNTRY_GP"])["TRANX_TTL"].sum().reset_index()

transactions_grouped_daily_country.rename(columns={
    "CAL_DAY": "DATE",
    "CALC_COUNTRY_GP":"COUNTRY",
    "TRANX_TTL": "TRANSACTIONS"
}, inplace=True)
transactions_grouped_daily_country.head()
# %% Transactions By Target Persona 
transactions_grouped_daily_targetpersona_country = transactions.groupby(["is_target_persona","CAL_DAY","CALC_COUNTRY_GP"])["TRANX_TTL"].sum().reset_index().rename(columns={
        "CAL_DAY": "DATE",
        "CALC_COUNTRY_GP":"COUNTRY",
        "TRANX_TTL": "TRANSACTIONS"
    })


# pivot target vs non-target into separate columns
transactions_grouped_daily_country_pivoted_targetpersona = (
    transactions_grouped_daily_targetpersona_country
    .pivot(
        index=['DATE', 'COUNTRY'],
        columns='is_target_persona',
        values='TRANSACTIONS'
    )
    .rename(columns={0: 'transactions_non_target', 1: 'transactions_target'})
    .reset_index()
    .fillna(0)

)

print("Target Persona Pivoted DF:")
print(transactions_grouped_daily_country_pivoted_targetpersona.head())

# %% Transactions by Category
import pandas as pd

# Set the category tag, seperate the low transaction value catagory
low_value_categories = ['FOOD & BEVERAGE', 'RESTAURANTS']
transactions['category_type'] = transactions['MCH3'].apply(
    lambda x: 'low_value_category' if x in low_value_categories else 'high_value_category'
)

transactions_grouped_daily_country_by_category = transactions.groupby(
    ["CAL_DAY", "CALC_COUNTRY_GP", "category_type"]
)["TRANX_TTL"].sum().reset_index()

# Rename the columns
transactions_grouped_daily_country_by_category.rename(columns={
    "CAL_DAY": "DATE",
    "CALC_COUNTRY_GP": "COUNTRY",
    "TRANX_TTL": "TRANSACTIONS"
}, inplace=True)

# Pivot data so that high and low value categories are separate columns
transactions_grouped_daily_country_by_category = (
    transactions_grouped_daily_country_by_category
    .pivot(
        index=['DATE', 'COUNTRY'],
        columns='category_type',
        values='TRANSACTIONS'
    )
    .reset_index()
    .fillna(0)
)

# Add total transaction column
transactions_grouped_daily_country_by_category['TRANSACTIONS_TOTAL'] = (
    transactions_grouped_daily_country_by_category['high_value_category'] + 
    transactions_grouped_daily_country_by_category['low_value_category']
)

print("By Category value DF:")
print(transactions_grouped_daily_country_by_category.head())

# %% Transactions by Tier
import pandas as pd

# 1. Define the tier hierarchy and make TIER_LATEST an ordered categorical
tier_order = [
    'Elite',
    'Platinum',
    'Black',
    'Gold',
    'Bronze',
    'Green',
    'Green 0',
    'Non Rewards'
]
transactions['TIER_LATEST'] = pd.Categorical(
    transactions['TIER_LATEST'],
    categories=tier_order,
    ordered=True
)

# 2. Sum TRANX_TTL by date, country and tier
agg = (
    transactions
    .groupby(['CAL_DAY', 'CALC_COUNTRY_GP', 'TIER_LATEST'], as_index=False)
    ['TRANX_TTL']
    .sum()
)

# 3. Pivot so each tier is its own column
wide = (
    agg
    .pivot(index=['CAL_DAY', 'CALC_COUNTRY_GP'],
           columns='TIER_LATEST',
           values='TRANX_TTL')
    .fillna(0)
    .reset_index()
)

# 4. Build “and above” columns by summing all tiers at or above each level
for tier in ['Bronze', 'Gold', 'Black', 'Platinum', 'Elite']:
    higher = tier_order[: tier_order.index(tier) + 1 ]
    wide[f'transactions_{tier.lower().replace(" ", "_")}_and_above'] = wide[higher].sum(axis=1)

# 5. (Optionally) drop the individual-tier columns now that you have the “and above” totals
cols_to_drop = tier_order
transactions_grouped_daily_country_pivoted_tiers = wide.drop(columns=cols_to_drop).rename(columns={
        "CAL_DAY": "DATE",
        "CALC_COUNTRY_GP":"COUNTRY",
        "TRANX_TTL": "TRANSACTIONS"
    })

# result now has: CAL_DAY, CALC_COUNTRY_GP, 
#    ttl_bronze_and_above, ttl_gold_and_above, ttl_black_and_above, ttl_platinum_and_above, ttl_elite_and_above
print("Tier Level DF:")
print(transactions_grouped_daily_country_pivoted_tiers.head())
# %% -------- Import Transactions and Group --------
# Merge the transaction and flight data by date
merged_date_country = pd.merge(transactions_grouped_daily_country, flights_grouped_daily_trip_origin, on=["DATE",'COUNTRY'], how="inner")

merged_date_country = pd.merge(merged_date_country, flights_airport, on=["DATE",'COUNTRY'], how="left")
merged_date_country = pd.merge(merged_date_country, flights_cabin, on=["DATE",'COUNTRY'], how="left")
merged_date_country = pd.merge(merged_date_country, transactions_grouped_daily_country_pivoted_targetpersona, on=["DATE",'COUNTRY'], how="left")
merged_date_country = pd.merge(merged_date_country, transactions_grouped_daily_country_pivoted_tiers, on=["DATE",'COUNTRY'], how="left")

merged_week_country = merged_date_country.groupby([pd.Grouper(key='DATE',freq='W-MON'),'COUNTRY'],
                                                 as_index = False).sum()

merged_week_country.to_csv(r"C:\Users\mkant\Documents\Intro to Python\CODE\LondonLab Data\merged_week_country.csv")

