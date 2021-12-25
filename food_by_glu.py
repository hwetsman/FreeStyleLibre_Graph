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


def Dedup_and_Sort(df):
    """ This function drops the duplicate rows in the df and sorts the values by
    the DateTime column in an ascending fashion.
    input: pandas df
    output: pandas df
    """
    df.drop_duplicates(inplace=True)
    df = df.sort_values(by='DateTime', ascending=True)
    return df


def Create_Food_Dict(df):
    """ This function finds the meds in the Notes column and creates a list of
    them. It then creates a df of only those rows that have a note in Notes
    col. Then, iterating the food list, it gets the specific food and number of
    times it appears in the dataset. It then creates a dictionary with food as
    the key and number of times it appears the value.
    input: pandas df
    output: python dict
    """
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
        raw_list = list(set(temp_df.Notes.tolist()))
        # remove nan from list
        final_list = [x for x in raw_list if pd.isnull(x) == False]
        # if there is another note in those rows discard the tmep_df
        if len(final_list) == 1:
            temp_df.Notes = final_list[0]
            temp_df = temp_df[~temp_df.Glucose.isnull()]
            dict1[start_time] = temp_df
    return dict1


def Create_Model(df, med):
    """
    This function takes a pandas df for a medication, index being the minutes
    post prandial. It creates a model from the df and adds an estimated glu
    col with the name of the medicine as the col name. It then returns that
    processed df.
    input: pandas df and a str of the mediction name
    output: pandas df
    """
    result = sm.ols(formula="Glucose ~ np.power(Minutes, 2) + Minutes", data=df).fit()
    a = result.params['np.power(Minutes, 2)']
    intercept = result.params['Intercept']
    b = result.params['Minutes']
    df[med] = a*df.index**2+b*df.index+intercept
    return df


def Feature_Eng(df):
    """
    This function takes the input df, drops unneeded columns, renames others,
    normalizes Notes col by lowering capital letters, and combining the three
    glucose measures into a single glucose column.
    input: pandas df
    output: pandas df
    """
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


def Create_Med_DF(p_df, med):
    """
    This function takes in a df and a dictionary. It gets the start and end
    dates from the dictionary and returns a deduplicated df between those dates.
    input:pandas df and the med dictionary
    output:pandas df
    """
    print('\nCreating med df...')
    start_date = pd.to_datetime(med.get('start_date'), format="%m-%d-%Y %I:%M %p")
    end_date = med.get('end_date')
    p_df.set_index('DateTime', inplace=True, drop=True)
    p_df = p_df[p_df.index >= start_date]
    p_df = p_df[p_df.index <= end_date]
    p_df.reset_index(inplace=True)
    p_df.drop_duplicates(inplace=True)
    df['DateTime'] = pd.to_datetime(df['DateTime'], format="%m-%d-%Y %I:%M %p")
    p_df = p_df.sort_values(by='DateTime', ascending=True)
    return p_df


def Combine_Med_DFs(dict_of_dfs):
    """
    This script takes the post-prandial dfs for a specific medication and c
    ombines them to make a single plot_df.
    input: python dictionary of dfs for a single med
    output: pandas df
    """
    plot_df = pd.DataFrame()
    for k, v in dict_of_dfs.items():
        plot_df = plot_df.append(v)
    plot_df = plot_df.groupby('Minutes')['Glucose'].mean()
    plot_df = pd.DataFrame(plot_df)
    plot_df.reset_index(inplace=True, drop=False)
    return plot_df


def Normalize_DFs(dict_of_dfs):
    """
    This function iterates through a dictionary of post-prandial dataframes,
    determines the start times, and converts those into minutes since meal started.
    It also takes the time zero glucose, converts it to 0 and subtracts it from
    all the other glucose values. This normalizes all the dfs for plotting from
    0 min, 0 glucose origin.
    input: dictionary of pandas dataframes
    output: dictionary of pandas dataframes
    """
    for k, v in dict_of_dfs.items():
        start_time = v['DateTime'].tolist()[0]
        start = v['Glucose'].tolist()[0]
        v.Glucose = (v.Glucose - start).astype(int)
        v['Time_Delta'] = v.DateTime - start_time
        v['Minutes'] = (v.Time_Delta.dt.seconds/60).astype(int)
        nv = v[['Minutes', 'Glucose']]
        dict_of_dfs[k] = nv
    return dict_of_dfs


# get most recent data
path = './most_recent_data/'
# files = os.listdir(path)
file = os.listdir(path)[0]

st.write('If you want to use your own data, click the button below or continue on with the sample data.')
input_needed = st.button('Use your own data')
if input_needed:
    uploaded_file = st.file_uploader("Choose a file")
    file = uploaded_file
else:
    file = os.listdir(path)[0]

st.write('Use the sliders and calendar inputs on the sidebar to filter the data. Scroll down the sidebar to see them all.')
st.write('In certain cases, foods you choose can be invalidated afterwards because of another food eaten \
within two hours. If this happens, a big red square with a lot of text will appear. Just move the slider \
to another food.')


# create df
df = pd.read_csv(path+file, header=1)

# convert timestamps to datetime
print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")

# Engineer Features
print('\nDropping unneeded columns...')
df = Feature_Eng(df)

# Limit records
print('\nDropping and organizing records...')
df = Dedup_and_Sort(df)

# get names of meds into streamlit
# cholestiramine = {'name': 'CLSM', 'start_date': '2021-8-17', 'end_date': '2021-10-13'}
# metformin = {'name': 'MTFM', 'start_date': '2021-9-20', 'end_date': '2021-10-16'}
# CoQ_10 = {'name': 'CoQ_10', 'start_date': '2021-11-11', 'end_date': '2021-11-21'}
# ezetimibe = {'name': 'EZTMB', 'start_date': '2021-11-27',
#              'end_date': datetime.today().date().strftime('%Y-%m-%d')}
# meds = [cholestiramine, metformin, CoQ_10, ezetimibe]
# set up empty med_dicts
med1 = {}
med2 = {}
# get input for med1
med1_name = st.sidebar.text_input('Add Med1', value='Metformin')
med1_start = pd.to_datetime(st.sidebar.date_input('Start Date for Med1', pd.to_datetime('2021-09-20'),
                                                  df['DateTime'].min(), df['DateTime'].max()))
med1_end = pd.to_datetime(st.sidebar.date_input('End Date for Med1', pd.to_datetime('2021-10-16'),
                                                df['DateTime'].min(), df['DateTime'].max()))
# get input for med2
med2_name = st.sidebar.text_input('Add Med2', value='CoQ10')
med2_start = pd.to_datetime(st.sidebar.date_input('Start Date for Med2', pd.to_datetime('2021-11-11'),
                                                  df['DateTime'].min(), df['DateTime'].max()))
med2_end = pd.to_datetime(st.sidebar.date_input('End Date for Med2', pd.to_datetime('2021-11-21'),
                                                df['DateTime'].min(), df['DateTime'].max()))
# create list of med_dicts
med_names = []
if med1_name != '':
    med1['name'] = med1_name
    med1['start_date'] = med1_start
    med1['end_date'] = med1_end
    med_names.append(med1)
if med2_name != '':
    med2['name'] = med2_name
    med2['start_date'] = med2_start
    med2['end_date'] = med2_end
meds = [med1, med2]

# create med_df
med1_df = Create_Med_DF(df.copy(), med1)
med2_df = Create_Med_DF(df.copy(), med2)

# create food_dict
food_dict = Create_Food_Dict(df)
med1_food_dict = Create_Food_Dict(med1_df)
med2_food_dict = Create_Food_Dict(med2_df)

# create list of foods
med1_list = [x for x in med1_food_dict]
med2_list = [x for x in med2_food_dict]
list_of_plottable_foods = [x for x in med1_list if x in med2_list]

print(f'These foods are in the database for both meds and so may be worth plotting:')
food = st.sidebar.select_slider('Available Foods', list_of_plottable_foods).lower()

# find the indexes at which the food appears in df.Notes
index_list = Get_Index_List(df, food)
med1_index_list = Get_Index_List(med1_df, food)
med2_index_list = Get_Index_List(med2_df, food)

# iterate the index_list to create a list of post prandial dfs
print('\nCreating post prandial dataframes...')
dict_of_dfs = Create_Food_DFs(df, index_list)
med1_dict_of_dfs = Create_Food_DFs(med1_df, med1_index_list)
med2_dict_of_dfs = Create_Food_DFs(med2_df, med2_index_list)

# Normalize Med_dfs for glucose and time
med1_dict_of_dfs = Normalize_DFs(med1_dict_of_dfs)
med2_dict_of_dfs = Normalize_DFs(med2_dict_of_dfs)

# combine into one df for each med
med1_plot_df = Combine_Med_DFs(med1_dict_of_dfs)
med2_plot_df = Combine_Med_DFs(med2_dict_of_dfs)

# create estimated model for each med
med1_plot_df = Create_Model(med1_plot_df, med1_name)
med2_plot_df = Create_Model(med2_plot_df, med2_name)

# engineer med_plots for merging
med1_plot_df.set_index('Minutes', inplace=True, drop=True)
med1_plot_df.drop('Glucose', inplace=True, axis=1)
med2_plot_df.set_index('Minutes', inplace=True, drop=True)
med2_plot_df.drop('Glucose', inplace=True, axis=1)
# create combined plot data
plot_data = pd.concat([med1_plot_df, med2_plot_df], axis=1)

# create fig and plot
fig, ax = plt.subplots()
x = plot_data.index
y1 = plot_data[med1_name]
y2 = plot_data[med2_name]
ax.plot(x, y1, label=med1_name)
ax.plot(x, y2, label=med2_name)
ax.set_xlabel('Minutes From First Bite')
ax.set_ylabel('Relative Glucose Level (mg/dL)')
ax.legend()
st.pyplot(fig)
