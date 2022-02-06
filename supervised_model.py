#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sunday Feb 06 2022

@author: howardwetsman
This script imports a file from the latest_data dir.

To do: import data -done
    prepare data
    initialize model
    visualize outcome
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


def Dedup_and_Sort(df):
    """ This function drops the duplicate rows in the df and sorts the values by
    the DateTime column in an ascending fashion.
    input: pandas df
    output: pandas df
    """
    df.drop_duplicates(inplace=True)
    df = df.sort_values(by='DateTime', ascending=True)
    return df


# IMPORT DATA
# get most recent data
path = './most_recent_data/'
# files = os.listdir(path)
file = os.listdir(path)[0]
# create df
df = pd.read_csv(path+file, header=1)

# PREPARE DATA
# convert timestamps to datetime
print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")
# Engineer Features
print('\nDropping unneeded columns...')
df = Feature_Eng(df)

print(df)
