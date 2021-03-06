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
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import streamlit as st

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
    # print('\nCombining measurements...')
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


def Create_Std_DF(df):
    std_df = df.groupby(
        pd.Grouper(freq='d')).std().dropna(how='all')
    std_df = std_df[['Glucose']]
    return std_df


def Limit_to_Current(df, start_date, end_date):
    df.set_index('Device Timestamp', inplace=True, drop=True)
    # print(type(df.index[0]))
    df = df[df.index >= start_date]
    df = df[df.index <= end_date]
    df.reset_index(inplace=True)
    return df


def Set_Meds(avg_df, meds):
    # set med cols to zeros
    for med in meds:
        name = med.get('name')
        avg_df[name] = 0
        start = med.get('start_date')
        start_year, start_month, start_day = start.split('-')
        end = med.get('end_date')
        end_year, end_month, end_day = end.split('-')
        days = np.arange(datetime(int(start_year), int(start_month), int(start_day)), datetime(
            int(end_year), int(end_month), int(end_day)), timedelta(days=1)).astype(datetime)
        for date in days:
            if date in avg_df.index:
                avg_df.loc[date, name] = 200
            else:
                pass
    # print(avg_df)
    # add 1's where appropriate
    return avg_df


st.sidebar.write('Pleae select the start and end dates if you want to change the range of the graph.  \
To enlarge the size of the graph put your mouse over the hamburger menu in the upper right, select \
settings, and select "wide mode".')
cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': '2021-11-21'}
ezetimibe = {'name': 'EZTMB', 'start_date': '2021-11-27',
             'end_date': datetime.today().date().strftime('%Y-%m-%d')}
NAD = {'name': 'NAD', 'start_date': '2022-06-25', 'end_date': '2022-07-18'}
cromolyn = {'name': 'CROM', 'start_date': '2022-07-14', 'end_date': '2022-07-21'}
breo = {'name': 'BREO', 'start_date': '2022-06-08', 'end_date': '2022-06-24'}
meds = [cholestiramine, metformin, CoQ_10, ezetimibe, NAD, cromolyn, breo]

# get most recent data
path = './most_recent_data/'
files = os.listdir(path)
# print(files)
# create df
df = pd.DataFrame()
for file in files:
    print(f'\nLoading file {file}...')
    temp = pd.read_csv(path+file, header=1, low_memory=False)
    df = df.append(temp)

# prune df
# print('\nDropping unneeded columns...')
df.drop(['Device', 'Serial Number',
        'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
         'Carbohydrates (grams)', 'Carbohydrates (servings)',
         'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
         'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
         'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)

# convert timestamps to datetime
# print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")

default_start = df['Device Timestamp'].min()
start_date = pd.to_datetime(st.sidebar.date_input('Start_Date', value=default_start))
default_end = df['Device Timestamp'].max()
end_date = pd.to_datetime(st.sidebar.date_input('End_Date', value=default_end))

df = Limit_to_Current(df, start_date, end_date)
# print('Limited to Current...')
# create df.Glu from measures
df = Combine_Glu(df)


######################################
# to do: drop duplicate index entries
df.drop_duplicates(inplace=True)
######################################


# create ave_df for mean glucose
avg_df = Create_Avg_DF(df)
# print(avg_df)

# print(df)
# create std_df for mean glucose
std_df = Create_Std_DF(df)
# print(std_df)


# add meds to the df
avg_df = Set_Meds(avg_df, meds)

# print('\nGenerating plot...')
fig, ax = plt.subplots(figsize=(16, 10))
sns.set_style('dark')
ax.plot(df.index, df['Glucose'], label='Glu', alpha=.4)
# mean
avg_df['rolling'] = avg_df.Glucose.rolling(7).mean().shift(-3)
sns.lineplot(x=avg_df.index, y='rolling', data=avg_df)
# std dev
plt.fill_between(avg_df.index, avg_df['rolling'] + std_df['Glucose']/2,
                 avg_df.Glucose - std_df.Glucose/2, alpha=0.8, color='lightskyblue')
print(avg_df)
med_num = len(meds)
med_colors = ['red', 'blue', 'green', 'gold', 'purple', 'pink', 'brown', 'turquoise']
for i in range(med_num):
    med = meds[i]
    med_start = pd.to_datetime(med.get('start_date'))
    med_end = pd.to_datetime(med.get('end_date'))
    name = med.get('name')
    med_df = avg_df[avg_df[name] > 0]
    if med_df.shape[0] == 0:
        pass
    else:
        print(name)
        print(med_df)
        avg = int(med_df['Glucose'].mean())
        label = f'{name} - {avg}'

    # if med_end is before graph start
    if max(med_end, start_date) == start_date:
        pass
    else:  # add med to bottom of graph
        plt.hlines(3*i, max(med_start, start_date), med_end, linestyles='solid', alpha=1,
                   linewidth=6, label=label, color=med_colors[i])

# horizontal lines
plt.hlines(110, avg_df.index.min(), avg_df.index.max(),
           colors='red', linestyles='dotted', alpha=.4)
plt.hlines(75, avg_df.index.min(), avg_df.index.max(),
           colors='red', linestyles='dotted', alpha=.4)
plt.hlines(100, avg_df.index.min(), avg_df.index.max(),
           colors='red', linestyles='solid', linewidth=.7)
plt.hlines(150, avg_df.index.min(), avg_df.index.max(),
           colors='red', linestyles='solid', linewidth=.7)
# xticks
plt.xticks(rotation='vertical')
plt.title('Glucose by Date')
# legend
plt.legend(loc='upper left')
# plt.show()
st.pyplot(fig)


#
