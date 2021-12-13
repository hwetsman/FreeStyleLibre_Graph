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
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import statsmodels.formula.api as sm
import time
import seaborn as sns
from datetime import datetime, timedelta
import numpy as np
import os
from matplotlib.pyplot import figure
import matplotlib
matplotlib.use('TkAgg')
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
    result = sm.ols(formula="Glu ~ np.power(Minutes, 2) + Minutes", data=plot_df).fit()
    a = result.params['np.power(Minutes, 2)']
    intercept = result.params['Intercept']
    b = result.params['Minutes']
    plot_df['Est'] = a*plot_df['Minutes']**2+b*plot_df['Minutes']+intercept
    return plot_df


def Feature_Eng(df):
    df.drop(['Device', 'Serial Number',
            'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
             'Carbohydrates (grams)', 'Carbohydrates (servings)',
             'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
             'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
             'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)
    df.rename(columns={'Device Timestamp': 'DateTime'}, inplace=True)
    df['Notes'] = df['Notes'].str.lower()
    df = Combine_Glu(df)
    return df


def Get_Index_List(df, food):
    index_list = df[df.Notes == food].index.tolist()
    return index_list


time0 = time.time()

# preparing for streamlit:

# get meds into streamlit
# get start and end dates into streamlit
# get cut off for foods into streamlit
filter = st.sidebar.slider('Cutoff for Food', 1, 100, 10)
st.write('If you want to use your own data, click the button below or continue on with the sample data.')
st.button('Use your own data')
st.write('Use the sliders and calendar inputs on the sidebar to filter the data.')
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

# get start_date for df filtering
start_date = pd.to_datetime(st.sidebar.date_input('Start Date for Filtering', df['Device Timestamp'].min(),
                                                  df['Device Timestamp'].min(), df['Device Timestamp'].max()))

# Engineer Features
print('\nDropping unneeded columns...')
df = Feature_Eng(df)
print(df.head())

# get names of meds into streamlit
med_names = []
# cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
# metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
# CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': '2021-11-21'}
# ezetimibe = {'name': 'EZTMB', 'start_date': '2021-11-27',
#              'end_date': datetime.today().date().strftime('%Y-%m-%d')}
# meds = [cholestiramine, metformin, CoQ_10, ezetimibe]
med1 = {}
med2 = {}
med1_name = st.sidebar.text_input('Add Med1')
med1_start = pd.to_datetime(st.sidebar.date_input('Start Date for Med1', start_date,
                                                  start_date, df['DateTime'].max()))
med1_end = pd.to_datetime(st.sidebar.date_input('End Date for Med1', df['DateTime'].max(),
                                                start_date, df['DateTime'].max()))
med2_name = st.sidebar.text_input('Add Med2')
med2_start = pd.to_datetime(st.sidebar.date_input('Start Date for Med2', start_date,
                                                  start_date, df['DateTime'].max()))
med2_end = pd.to_datetime(st.sidebar.date_input('End Date for Med2', df['DateTime'].max(),
                                                start_date, df['DateTime'].max()))

if med1_name != '':
    med1['name'] = med1_name
    med1['start_date'] = med1_start
    med1['end_date'] = med1_end
    med_names.append(med1)
if med2_name != '':
    print(med2_name)
    med2['name'] = med2_name
    med2['start_date'] = med2_start
    med2['end_date'] = med2_end
meds = [med1, med2]


# create med_df


def Create_Med_DF(p_df, med):
    start_date = med.get('start_date')
    end_date = med.get('end_date')
    p_df.set_index('DateTime', inplace=True, drop=True)
    p_df = p_df[p_df.index >= start_date]
    p_df = p_df[p_df.index <= start_date]
    p_df.reset_index(inplace=True)
    p_df.drop_duplicates(inplace=True)
    df['DateTime'] = pd.to_datetime(df['DateTime'], format="%m-%d-%Y %I:%M %p")
    p_df = p_df.sort_values(by='DateTime', ascending=True)
    return p_df


med1_df = Create_Med_DF(df.copy(), med1)
med2_df = Create_Med_DF(df.copy(), med2)

print(med1_df)


# Limit records
print('\nDropping and organizing records...')
df = Limit_to_Current(df, start_date)

# save as interim
df.to_csv('df_sorted.csv', index=False)
org_df = df
# create food_dict
food_dict = Create_Food_Dict(df)

# list of foods
# at this point ask the user for the number of occurances they want to filter by
# in this case the filter is set hard below for speed in development
# filter = 10
list_of_plottable_foods = Trim_Food_Dict(food_dict, filter)
print(f'These foods are in the database more than {filter} times and so may be worth plotting:')
food = st.sidebar.select_slider('Available Foods', list_of_plottable_foods).lower()
# for food in list_of_plottable_foods:
#     print(food)

# in web based iteration we would present this list to the user and let them choose in a drop down.
# here we will hard code the food to use

# food = 'Grits x 2'
# food = 'Crackers and pb'
# food = 'pizza'
# food = 'grits'
# food = 'cheese'
# food = 'crackers'
# food = food.lower()
# list_of_plotable_foods = ['grits x 2', 'crackers and pb', 'pizza', 'grits', 'cheese', 'crackers']
# for food in list_of_plotable_foods:
df = org_df
# get dfs of 2 hour post prandial periods after eating 'food'
# find the indexes at which the food appears in df.Notes
index_list = Get_Index_List(df, food)
st.write(f"'{food}' occurs {len(index_list)} times in the dataset.")
print(f'{food.title()} occurs {len(index_list)} times in the dataset')

# iterate the index_list to create a list of post prandial dfs
print('\nCreating post prandial dataframes...')
dict_of_dfs = Create_Food_DFs(df, index_list)

# want to add an interation of all the indeces
# to create a no_meds dict of dfs to add to pp_med_dict latter

# iterate dict_of_dfs and create med_dicts of 2 hr pp dfs
print('\nAdding meds to post prandial dataframes...')
pp_med_dict = {}
for med in meds:
    ind_med_dict = {}
    name = med.get('name')

    start = pd.to_datetime(med.get('start_date')).date()
    end = pd.to_datetime(med.get('end_date')).date()
    for k, v in dict_of_dfs.items():
        update_dict = {}
        date_of_food = k.date()
        if start <= date_of_food <= end:
            update_dict[k] = v
            ind_med_dict.update(update_dict)

    if len(ind_med_dict) >= 1:
        pp_med_dict[name] = {}
        pp_med_dict[name].update(ind_med_dict)
    else:
        pass

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
for name in pp_med_dict:
    plot_df = pd.DataFrame(pp_med_dict.get(name))
    plot_df.columns = ['Glu']
    plot_df.reset_index(drop=False, inplace=True)
    plot_df = Create_Model(plot_df)
    plot_df.set_index('Minutes', inplace=True, drop=True)
    pp_med_dict[name] = plot_df

# for name in pp_med_dict:
#     print(name)
#     print(pp_med_dict.get(name))
#     print()

print('\nGetting data to plot...')
meds_to_plot = {}
for name in pp_med_dict:
    df = pp_med_dict.get(name)
    # df.drop('Glu', axis=1, inplace=True)
    new_dict = df.to_dict().get('Est')
    meds_to_plot[name] = new_dict

# normalize the meds_to_plot dicts:
for med in meds_to_plot:
    print(med)
    transformed_dict = {}
    raw_dict = meds_to_plot.get(med)
    start = raw_dict.get(0)
    for k, v in raw_dict.items():
        new_value = v-start
        transformed_dict[k] = new_value
    meds_to_plot[med] = transformed_dict

time1 = time.time()
print(f'This took {time1-time0} seconds.')
# plot them out with 2 hours on the x axis and a line for each med tracing out
# fig, ax = plt.subplots()
# print(fig)
# for med in meds_to_plot:
#     xy_dict = meds_to_plot.get(med)
#     x = xy_dict.keys()
#     y = xy_dict.values()
#     st.line_chart(x, y)
#     # ax.plot(x, y, label=med)
# else:
#     pass
# fig.legend()
# fig.title(f"2-hr Glucose Pattern After '{food}'")
# fig.xlabel('Minutes')
# fig.ylabel('Glucose')
# plt.show()
plot_data = pd.DataFrame()
for med in meds_to_plot:
    xy_dict = meds_to_plot.get(med)
    index = xy_dict.keys()
    temp_df = pd.DataFrame(xy_dict.values(), index=index, columns=[med])
    print(temp_df.head())
    plot_data = pd.concat([plot_data, temp_df], axis=1)
    print(plot_data.head())
print(plot_data)
st.line_chart(plot_data)
