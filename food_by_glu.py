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
    #df.sort_values(by='Device Timestamp', inplace=True)
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
    df.set_index('DateTime', inplace=True, drop=True)
    print(type(df.index[0]))
    df = df[df.index >= start_date]
    df.reset_index(inplace=True)
    df.drop_duplicates(inplace=True)
    df = df.sort_values(by='DateTime', ascending=True)
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


def Feature_Eng(df):
    df.drop(['Device', 'Serial Number',
            'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
             'Carbohydrates (grams)', 'Carbohydrates (servings)',
             'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
             'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
             'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)
    df.rename(columns={'Device Timestamp': 'DateTime'}, inplace=True)
    df = Combine_Glu(df)
    return df


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


# Engineer Features
print('\nDropping unneeded columns...')
print(df)
df = Feature_Eng(df)

#Limit records
print('\nDropping and organizing records...')
df = Limit_to_Current(df, start_date)

#save as interim
df.to_csv('df_sorted.csv', index=False)
print(df)


#create food_dict
food_dict = Create_Food_Dict(df)
print(food_dict)

#list of foods
list_of_plottable_foods = [x for x in food_dict if food_dict.get(x) > 5]
print('These foods are in the database more than 5 times and so may be worth plotting:')
for food in list_of_plottable_foods:
    print(food)
# in web based iteration we would present this list to the user and let them choose in a drop down.
# here we will hard code the food to use
food = 'Grits x 2'
print(f'\nYou selected {food}.')


# get dfs of 2 hour post prandial periods after eating 'food'
# find the indexes at which the food appears in df.Notes
index_list = df[df.Notes == food].index.tolist()
print(f'There are {len(index_list)} entries in your index list')

# iterate the index_list to create a list of plottable dfs
# list_of_dfs = []
dict_of_dfs = {}
for idx in index_list:
    print(f'The first index is {idx}.')
    # find the start time for these indexes
    start_time = df['DateTime'][idx]
    print(f'The start time is {start_time}.')
    end_time = start_time + pd.DateOffset(hours=2)
    print(f'The end time is {end_time}.')

    # select the rows from those instances to 2 hours after those instances as temp_df
    temp_df = df[(df['DateTime'] >= start_time) & (df['DateTime'] <= end_time)]
    # temp_df.dropna(thresh=2,inplace=True)
    print('Here is the temporary df')
    print(temp_df)

    #something is going wrong in this loop. i am not able to get the second index
    #to pull a time. I am getting an error saying the index needs to be an int
    #and it is. It works before the loop but the same index doesn't work after First
    #one.
    raw_list = list(set(temp_df.Notes.tolist()))
    print('here is the raw list')
    print(raw_list)
    # remove nan from list
    final_list = [x for x in raw_list if pd.isnull(x) == False]
    print('here is the list after removing NaNs.')
    print(final_list)


    # if there is another note in those rows discard the tmep_df
    if len(final_list) == 1:
        temp_df.Notes = final_list[0]
        temp_df=temp_df[~temp_df.Glucose.isnull()]
        dict_of_dfs[start_time] = temp_df
        print('appending it')
    else:
        print('not appending it')
# print(f'There are {len(list_of_dfs)} dfs in the list')
print(dict_of_dfs)


#iterate dict_of_dfs and create med_dicts of 2 hr pp dfs
pp_med_dict = {}

for med in meds:
    ind_med_dict={}
    name = med.get('name')
    pp_med_dict[name]={}
    start = pd.to_datetime(med.get('start_date'))
    end = pd.to_datetime(med.get('end_date'))
    print(name)
    for k,v in dict_of_dfs.items():
        update_dict={}
        date_of_food = k.date()
        print(date_of_food)
        if start <= date_of_food <= end:
            update_dict[k]=v
            ind_med_dict.update(update_dict)
    pp_med_dict[name].update(ind_med_dict)

print(pp_med_dict)

#normalize all glucose values to zero start
print('\n\n')
for name in pp_med_dict:
    print(name)
    dict_of_dfs = pp_med_dict.get(name)
    for k,v in dict_of_dfs.items():
        print(k)

        start_time = v['DateTime'].tolist()[0]
        start = v['Glucose'].tolist()[0]
        v.Glucose = (v.Glucose - start).astype(int)
        v['Time_Delta']= v.DateTime - start_time
        v['Minutes'] = (v.Time_Delta.dt.seconds/60).astype(int)
        nv = v[['Minutes','Glucose']]
        print(nv)
        # print(type(v.iloc[0,3]))

        #v['Minutes'] = v.Time_Delta.seconds/60
        #(td / np.timedelta64(1, 'D')).astype(int)
        dict_of_dfs[k]=nv
# for name in pp_med_dict:
#     print(name)
#     dict_of_dfs = pp_med_dict.get(name)
#     for k,v in dict_of_dfs.items():
#         print(k)
#         prin`t(v)
1/0

# get the glucose col as a list
# collect these lists in a dictionary per medication
# average them for each medication

# the glucose reaction to the food for each of those meds
meds_to_plot = {'CLSM': {0: 90, 13: 98, 28: 104, 43: 107, 58: 135,
                         73: 128, 88: 134, 95: 113, 100: 104, 107: 107, 117: 110, 119: 119},
                'CoQ_10': {0: 125, 10: 120, 25: 118, 40: 107, 55: 97,
                           70: 96, 85: 115, 100: 130, 115: 132},
                'None': {0: 96, 13: 100, 28: 101, 43: 105, 80: 112,
                         95: 110, 110: 110}
                }

# normalize the meds_to_plot dicts:
for med in meds_to_plot:
    transformed_dict = {}
    raw_dict = meds_to_plot.get(med)
    start = raw_dict.get(0)
    for k, v in raw_dict.items():
        new_value = v-start
        transformed_dict[k] = new_value
    meds_to_plot[med] = transformed_dict

# plot them out with 2 hours on the x axis and a line for each med tracing out
for med in meds_to_plot:
    xy_dict = meds_to_plot.get(med)
    x = xy_dict.keys()
    y = xy_dict.values()
    plt.plot(x, y, label=med)
    print(x)
    print(y)
else:
    pass
plt.legend()
plt.title(f"2-hr Glucose Pattern After '{food}'")
plt.xlabel('Minutes')
plt.ylabel('Glucose')
plt.show()
df = Combine_Glu(df)


1/0
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
