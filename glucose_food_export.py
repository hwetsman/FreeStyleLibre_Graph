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
    st.write('df before drop', df)
    df.drop(['Record Type',
             'Historic Glucose mg/dL',
             'Scan Glucose mg/dL',
             'Non-numeric Food'], inplace=True, axis=1)
    st.write('df after drop', df)
    df.columns = ['DateTime', 'Notes', 'Glucose']
    df.set_index('DateTime', inplace=True, drop=True)
    df.reset_index(inplace=True)
    return(df)


def Create_Avg_DF(df):
    df1 = df.set_index('DateTime', drop=True)
    avg_df = df1.groupby(
        pd.Grouper(freq='d')).mean().dropna(how='all')
    avg_df = avg_df[['Glucose']]
    st.write(avg_df)
    avg_df = avg_df.rename(columns={'Glucose': 'mean_glucose'})
    st.write(avg_df)
    return avg_df


def Create_Max_DF(df):
    df1 = df.set_index('DateTime', drop=True)
    max_df = df1.groupby(
        pd.Grouper(freq='d')).max().dropna(how='all')
    max_df = max_df[['Glucose']]
    max_df = max_df.rename(columns={'Glucose': 'max_glucose'})
    return max_df


st.set_page_config(layout="wide")

path = './most_recent_data/'
files = os.listdir(path)
#
#
# # create df
df = pd.DataFrame()
for file in files:
    print(f'\nLoading file {file}...')
    temp = pd.read_csv(path+file, header=1, low_memory=False)
    df = df.append(temp)
    print(f'appended {file} to df')
st.write(df)
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")
df.drop(['Device', 'Serial Number',
        'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
         'Carbohydrates (grams)', 'Carbohydrates (servings)',
         'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
         'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
         'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)

df1 = df.drop_duplicates()
glu_only = Combine_Glu(df1)
st.write('glu only', glu_only)
daily_average = Create_Avg_DF(glu_only)
st.write('average', daily_average)
st.write('glu only', glu_only)
daily_max = Create_Max_DF(glu_only)
st.write('max', daily_max)
