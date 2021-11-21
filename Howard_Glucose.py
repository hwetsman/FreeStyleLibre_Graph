#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 09:13:02 2021

@author: howardwetsman
"""
import os
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.expand_frame_repr', False)
pd.options.mode.chained_assignment = None  # default='warn'


def Combine_Glu(df):
    print('\nCombining measurements...')
    notes = df[df['Record Type'] >= 5]
    measures = df[df['Record Type'] <= 2]
    measures['Historic Glucose mg/dL'].fillna(value=0, inplace=True)
    measures['Scan Glucose mg/dL'].fillna(value=0, inplace=True)
    measures.loc[:, 'Glu'] = measures.loc[:, 'Scan Glucose mg/dL'] + \
        measures.loc[:, 'Historic Glucose mg/dL']
    df = measures.append(notes)
    df.sort_values(by='Device Timestamp', inplace=True)
    df.drop(['Record Type',
             'Historic Glucose mg/dL',
             'Scan Glucose mg/dL',
             'Non-numeric Food'], inplace=True, axis=1)
    df.columns = ['DateTime', 'Notes', 'Glucose']
    df.set_index('DateTime', inplace=True, drop=True)
    df.reset_index(inplace=True)
    return(df)


def Limit_to_Current(df):
    df.set_index('DateTime', inplace=True, drop=True)
    df = df['2021-08-27 00:00:00':]
    df.reset_index(inplace=True)
    return df


# get most recent data
path = './most_recent_data/'
files = os.listdir(path)

# create df
df = pd.DataFrame()
for file in files:
    print(f'\nLoading file {file}...')
    temp = pd.read_csv(path+file, header=1)
    df = df.append(temp)

# prune df
print('\nDropping unneeded columns...')
df.drop(['Device', 'Serial Number',
        'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
         'Carbohydrates (grams)', 'Carbohydrates (servings)',
         'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
         'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
         'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)

# convert timestamps to datetime
print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'])
df.drop_duplicates(inplace=True)

# create df.Glu from measures
df = Combine_Glu(df)

# limit to current experiment
df = Limit_to_Current(df)

# add meds
print('\nAdding meds...')
cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': None}
meds = [cholestiramine, metformin, CoQ_10]
first_date = df['DateTime'].dt.date.min()
last_date = df['DateTime'].dt.date.max()

for med in meds:
    name = med.get('name')
    df[name] = 0
    start_date = med.get('start_date')
    end_date = med.get('end_date')
    if end_date == None:
        end_date = last_date
    dates = pd.date_range(start=str(start_date), end=str(
        end_date), freq="D").strftime('%Y-%m-%d').tolist()
    for idx, row in df.iterrows():
        d = df.loc[idx, 'DateTime']
        date = str(d.date())
        if date in dates:
            df.loc[idx, name] = 200

print('\nGenerating plot...')

figure(figsize=(15, 8))
plt.plot(df['DateTime'], df['Glucose'], label='Glu')
plt.xticks(rotation='vertical')

plt.plot(df['DateTime'], df['CLSM'], label='CLSM')
plt.xticks(rotation='vertical')

plt.plot(df['DateTime'], df['MTFM'], label='MTFM')
plt.xticks(rotation='vertical')

plt.plot(df['DateTime'], df['CoQ_10'], label='CoQ_10')
plt.xticks(rotation='vertical')

plt.legend(loc='upper left')
plt.show()


#
