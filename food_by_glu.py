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
import statsmodels.formula.api as sm
import time
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import os
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd
pd.options.mode.chained_assignment = None

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
    measures[['Historic Glucose mg/dL', 'Scan Glucose mg/dL']
             ] = measures[['Historic Glucose mg/dL', 'Scan Glucose mg/dL']].fillna(value=0)
    measures['Glu'] = measures.loc[:, ['Historic Glucose mg/dL', 'Scan Glucose mg/dL']].sum(axis=1)
    df = measures.append(notes)
    df.drop(['Record Type',
             'Historic Glucose mg/dL',
             'Scan Glucose mg/dL',
             'Non-numeric Food'], inplace=True, axis=1)
    df.columns = ['DateTime', 'Notes', 'Glucose']
    df.set_index('DateTime', inplace=True, drop=True)
    df.reset_index(inplace=True)
    return(df)


def Trim_Food_Dict(food_dict, occurances):
    """
    inputs(dict,int)
    food_dict (dict): a dictionary of foods in the dataset as key and the number of
    occurances of that food as the value
    occurances (int): the number of occurances the user wishes to use as the filter
    for the output list of foods
    ouput(list)
    The output is a list of foods occuring more often in the dataset than the
    occurances cut off.
    """
    list_of_plottable_foods = [x for x in food_dict if food_dict.get(x) > occurances]
    return list_of_plottable_foods


def Limit_to_Current(df, start_date):
    df.set_index('DateTime', inplace=True, drop=True)
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


def Create_Food_DFs(df, index_list):
    """
    Input:
    df (pandas dataframe): The dataframe being suggested
    index_list (python list): a list of indeces in the df where food notations
    appear
    Action: finds the time at which the food is listed, calculates 2 hours
    after the food is listed, grabs a temp_df of the two hour post prandial readings,
    determines if any other factors were listed during those two hours and if so
    omit that df from consideration, and then appending the df to a dictionary.
    Output:
    dict1 (python dictionary) with unique start time as key and df as value
    """
    dict1 = {}
    for idx in index_list:
        # find the start time for these indexes
        start_time = df['DateTime'][idx]
        end_time = start_time + pd.DateOffset(hours=2)
        # select the rows from those instances to 2 hours after those instances as temp_df
        temp_df = df[(df['DateTime'] >= start_time) & (df['DateTime'] <= end_time)]
        # temp_df.dropna(thresh=2,inplace=True)
        raw_list = list(set(temp_df.Notes.tolist()))
        # remove nan from list
        final_list = [x for x in raw_list if pd.isnull(x) == False]
        # if there is another note in those rows discard the tmep_df
        if len(final_list) == 1:
            temp_df.Notes = final_list[0]
            temp_df = temp_df[~temp_df.Glucose.isnull()]
            dict1[start_time] = temp_df
    return dict1


def Create_Model(df):
    result = sm.ols(formula="Glu ~ Minutes", data=plot_df).fit()
    intercept = result.params['Intercept']
    b = result.params['Minutes']
    plot_df['Est'] = b*plot_df['Minutes']+intercept
    return plot_df


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


time0 = time.time()
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
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")

# ask for input for start date
# start_date = pd.to_datetime(
# input("Please input a start date. If you want to limit your data set. The format is YYYY-MM-DD: "))
start_date = pd.to_datetime('2021-09-14')

# Engineer Features
print('\nDropping unneeded columns...')
df = Feature_Eng(df)

# Limit records
print('\nDropping and organizing records...')
df = Limit_to_Current(df, start_date)

# save as interim
df.to_csv('df_sorted.csv', index=False)

# create food_dict
food_dict = Create_Food_Dict(df)

# list of foods
# at this point ask the user for the number of occurances they want to filter by
# in this case the filter is set hard below for speed in development
filter = 5
list_of_plottable_foods = Trim_Food_Dict(food_dict, filter)
print(f'These foods are in the database more than {filter} times and so may be worth plotting:')
for food in list_of_plottable_foods:
    print(food)

# in web based iteration we would present this list to the user and let them choose in a drop down.
# here we will hard code the food to use
#food = 'Crackers'
food = 'Grits x 2'
# food = 'Ice cream'
print(f'\nYou selected {food}.')


# get dfs of 2 hour post prandial periods after eating 'food'
# find the indexes at which the food appears in df.Notes
index_list = df[df.Notes == food].index.tolist()
print(f'There are {len(index_list)} entries in your index list')

# iterate the index_list to create a list of post prandial dfs
print('\nCreating post prandial dataframes...')
dict_of_dfs = Create_Food_DFs(df, index_list)


# iterate dict_of_dfs and create med_dicts of 2 hr pp dfs
print('\nAdding meds to post prandial dataframes...')
pp_med_dict = {}
for med in meds:
    ind_med_dict = {}
    name = med.get('name')
    pp_med_dict[name] = {}
    start = pd.to_datetime(med.get('start_date'))
    end = pd.to_datetime(med.get('end_date'))
    for k, v in dict_of_dfs.items():
        update_dict = {}
        date_of_food = k.date()
        if start <= date_of_food <= end:
            update_dict[k] = v
            ind_med_dict.update(update_dict)
    pp_med_dict[name].update(ind_med_dict)

# normalize all glucose values to zero start
print('\nNormalizing glucose values...')
for name in pp_med_dict:
    dict_of_dfs = pp_med_dict.get(name)
    for k, v in dict_of_dfs.items():
        start_time = v['DateTime'].tolist()[0]
        start = v['Glucose'].tolist()[0]
        v.Glucose = (v.Glucose - start).astype(int)
        v['Time_Delta'] = v.DateTime - start_time
        v['Minutes'] = (v.Time_Delta.dt.seconds/60).astype(int)
        nv = v[['Minutes', 'Glucose']]
        dict_of_dfs[k] = nv

# combine all 2hr pp dfs for a med and get mean glucose for every minute
print('\nCombining all post prandial dataframes by med...')
for name in pp_med_dict:
    plot_df = pd.DataFrame()
    dict_of_dfs = pp_med_dict.get(name)
    for k, v in dict_of_dfs.items():
        plot_df = plot_df.append(v)
    plot_df = plot_df.groupby('Minutes')['Glucose'].mean()
    pp_med_dict[name] = plot_df


# create ols cols in dfs
print('working on ols...')
for name in pp_med_dict:
    print(name)
    plot_df = pd.DataFrame(pp_med_dict.get(name))
    plot_df.columns = ['Glu']
    plot_df.reset_index(drop=False, inplace=True)
    plot_df = Create_Model(plot_df)
    pp_med_dict[name] = plot_df

print('\nGetting data to plot...')
meds_to_plot = {}
for name in pp_med_dict:
    df = pp_med_dict.get(name)
    new_dict = df.to_dict()
    meds_to_plot[name] = new_dict

time1 = time.time()
print(f'This took {time1-time0} seconds.')
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
else:
    pass
plt.legend()
plt.title(f"2-hr Glucose Pattern After '{food}'")
plt.xlabel('Minutes')
plt.ylabel('Glucose')
plt.show()


#
