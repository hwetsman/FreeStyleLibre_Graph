#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 20 09:13:02 2021

@author: howardwetsman
To do: turn out put into a website
        create dropdown for date instead of text input
        interrogate Notes for food eaten
        Offer foods eaten to users
        create output showing foods eaten and 2hr pp by day
        allow input of start and stop dates for daily meds
        allow food graphs of 2 hour pp by meds
"""
import os
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
pd.set_option('display.expand_frame_repr', False)


def Combine_Glu(df):
    """ This function divides the df into measurements and notes where measurements
    are the rows created by either historical, scanned or input glucose readings.
    If first fills measurement columns with zeros for NaN's and then adds them
    together in a new 'Glucose' column. The two created df's are then appended,
    the unnecessary cols are dropped, the index is reset, and the df is
    returned.
    """
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


def Create_Avg_DF(df):
    df.set_index('DateTime', inplace=True, drop=True)
    avg_df = df.groupby(
        pd.Grouper(freq='d')).mean().dropna(how='all')
    ave_df = avg_df[['Glucose']]
    return avg_df


def Limit_to_Current(df, start_date):
    df.set_index('Device Timestamp', inplace=True, drop=True)
    print(type(df.index[0]))
    df = df[df.index >= start_date]
    df.reset_index(inplace=True)
    return df

def Set_Meds(df,meds):
    return meds


cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': '2021-11-21'}
meds = [cholestiramine,metformin,CoQ_10]

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

# ask for input for start date
start_date = pd.to_datetime(
    input("Please input a start date. If you want to limit your data set. The format is YYYY-MM-DD: "))
print(type(start_date))

df = Limit_to_Current(df, start_date)
# create df.Glu from measures
df = Combine_Glu(df)

# create ave_df for mean glucose
avg_df = Create_Avg_DF(df)

print('\nGenerating plot...')
figure(figsize=(15, 8))
plt.plot(df.index, df['Glucose'], label='Glu')
plt.plot(avg_df.index, avg_df['Glucose'], label='Mean')
plt.hlines(110, avg_df.index.min(), avg_df.index.max(), colors='red', linestyles='dashed')
plt.hlines(75, avg_df.index.min(), avg_df.index.max(), colors='red', linestyles='dashed')
plt.xticks(rotation='vertical')


plt.legend(loc='upper left')
plt.show()


#
