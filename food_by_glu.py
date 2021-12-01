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


def Create_Std_DF(df):
    # df.set_index('DateTime', inplace=True, drop=True)
    std_df = df.groupby(
        pd.Grouper(freq='d')).std().dropna(how='all')
    std_df = std_df[['Glucose']]
    return std_df


def Limit_to_Current(df, start_date):
    df.set_index('Device Timestamp', inplace=True, drop=True)
    print(type(df.index[0]))
    df = df[df.index >= start_date]
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
    print(avg_df)
    # add 1's where appropriate
    return avg_df


def Create_Food_Dict(df):
    food_dict = {}
    foods = list(set(df.Notes.tolist()))
    contains_notes = df[~df.Notes.isnull()]
    for food in foods:
        if isinstance(food, str):
            temp = contains_notes[contains_notes.Notes.str.contains(food)]
            if temp.shape[0] > 4:
                food_dict[food] = temp.shape[0]
    return food_dict


cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': '2021-11-21'}
meds = [cholestiramine, metformin, CoQ_10]

# get most recent data
path = './most_recent_data/'
files = os.listdir(path)

# create df
df = pd.DataFrame()
for file in files:
    print(f'\nLoading file {file}...')
    temp = pd.read_csv(path+file, header=1)
    df = df.append(temp)

# convert timestamps to datetime
print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'])

# ask for input for start date
# start_date = pd.to_datetime(
# input("Please input a start date. If you want to limit your data set. The format is YYYY-MM-DD: "))
start_date = pd.to_datetime('2021-09-14')
print(type(start_date))

df = Limit_to_Current(df, start_date)


# prune df
print('\nDropping unneeded columns...')
df.drop(['Device', 'Serial Number',
        'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
         'Carbohydrates (grams)', 'Carbohydrates (servings)',
         'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
         'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
         'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)

# create food_dict containing foods and number of times they occur in data
# food_dict = {}
# foods = list(set(df.Notes.tolist()))
# contains_notes = df[~df.Notes.isnull()]
# for food in foods:
#     if isinstance(food, str):
#         temp = contains_notes[contains_notes.Notes.str.contains(food)]
#         if temp.shape[0] > 4:
#             food_dict[food] = temp.shape[0]
# print(food_dict)

food_dict = Create_Food_Dict(df)

# for food,number in food_dict.items()
# find the indexes at which the food appears in df.Notes
# select the rows from those instances to 2 hours after those instances as temp_df
# if there is another note in those rows discard the tmep_df
# if the day it occurred is between start and stop of a med make that med in the med col
# get the glucose col as a list
# collect these lists in a dictionary per medication
# average them for each medication
# plot them out with 2 hours on the x axis and a line for each med tracing out
# the glucose reaction to the food for each of those meds


# create df.Glu from measures
df = Combine_Glu(df)


######################################
# to do: drop duplicate index entries
df.drop_duplicates(inplace=True)
######################################


# create ave_df for mean glucose
avg_df = Create_Avg_DF(df)
print(avg_df)


# create std_df for mean glucose
std_df = Create_Std_DF(df)
print(std_df)


# add meds to the df
avg_df = Set_Meds(avg_df, meds)

print('\nGenerating plot...')
figure(figsize=(15, 8))
# glucose
plt.plot(df.index, df['Glucose'], label='Glu', alpha=.4)
# mean
plt.plot(avg_df.index, avg_df['Glucose'], label='Mean')
# std dev
plt.fill_between(avg_df.index, avg_df['Glucose'] + std_df['Glucose']/2,
                 avg_df.Glucose - std_df.Glucose/2, alpha=0.8, color='lightskyblue')

med_num = len(meds)
med_colors = ['red', 'blue', 'green', 'gold', 'purple', 'pink']
for i in range(med_num):
    med = meds[i]
    start = pd.to_datetime(med.get('start_date'))
    if start < start_date:
        start = start_date
    else:
        pass
    end = pd.to_datetime(med.get('end_date'))
    name = med.get('name')
    plt.hlines(3*i, start, end, linestyles='solid', alpha=1,
               linewidth=6, label=name, color=med_colors[i])
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
# legend
plt.legend(loc='upper left')
plt.show()


#
