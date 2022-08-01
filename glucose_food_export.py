import os
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import seaborn as sns
import streamlit as st
# from nltk.corpus import stopwords


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
    df1 = df.set_index('DateTime', drop=True)
    avg_df = df1.groupby(
        pd.Grouper(freq='d')).mean().dropna(how='all')
    avg_df = avg_df[['Glucose']]
    avg_df = avg_df.rename(columns={'Glucose': 'mean_glucose'})
    return avg_df


def Create_Max_DF(df):
    df1 = df.set_index('DateTime', drop=True)
    max_df = df1.groupby(
        pd.Grouper(freq='d')).max().dropna(how='all')
    max_df = max_df[['Glucose']]
    max_df = max_df.rename(columns={'Glucose': 'max_glucose'})
    return max_df


def Get_Glu_By_Day(glu_only):
    daily_average = Create_Avg_DF(glu_only)
    daily_max = Create_Max_DF(glu_only)
    glu_by_day = pd.merge(daily_max, daily_average, on='DateTime', how='outer')
    glu_by_day.reset_index(inplace=True, drop=False)
    glu_by_day.rename(columns={'DateTime': 'date'}, inplace=True)
    return glu_by_day


def Combine_Notes(df1):
    notes_only = df1[['Notes', 'Device Timestamp']]
    notes_only = notes_only.rename(columns={'Device Timestamp': 'DateTime'})
    notes_only.Notes = notes_only.Notes.fillna('')
    notes_only.set_index('DateTime', inplace=True, drop=True)
    daily_notes = notes_only.groupby(pd.Grouper(freq='d'))[
        'Notes'].apply(' '.join).reset_index(drop=False)
    daily_notes['next'] = 0

    daily_notes.Notes = daily_notes.Notes.str.replace('with', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('from', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('and', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('piece of', '')
    daily_notes.Notes = daily_notes.Notes.str.replace(' w ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace(' x ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace(' mg ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace(' pb ', ' peanutbutter ')
    daily_notes.Notes = daily_notes.Notes.str.replace(' peanut butter ', ' peanutbutter ')
    daily_notes.Notes = daily_notes.Notes.str.replace('after', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('exercise', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('shower', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('meds', '')
    daily_notes.Notes = daily_notes.Notes.str.replace(' on ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('     ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('    ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('   ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('  ', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace(',', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('-', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('.', ' ')
    daily_notes.Notes = daily_notes.Notes.str.replace('finger stick', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('blood stick', '')
    daily_notes.Notes = daily_notes.Notes.str.replace('\d+', '')
    daily_notes.Notes = daily_notes.Notes.str.lower()
    string = set(' '.join(daily_notes.Notes).split(' '))
    drop = ['', 'reveratrol', 'in', 'dao', 'a', 'l-methylfolate', 'cromalyn', 'glutathione', 'ago', 'flonase',
            'little', 'fast', 'claritinzantac', 'ten', 'note', 'yesterday', 'chromium', 'took', 'cold', 'feeling', 'zantac',
            'humans', 'finger', 'heat', 'hot', 'kind', 'started', 'tylenol', 'cholestiramine', 'strength', 'stick', 'that',
            'bite', 'without', 'claritin', 'vsl', "mosca's", 'baby', 'after', 'lunch', 'one', 'exercise', 'this', 'black',
            'all', 'zantaz', 'from', 'local', 'tow', 'x', ' ', 'scoop', 'vit', 'soft', 'string', 'glucose', 'big', 'chromium',
            'two', 'got', 'enzymes', 'enlytezantac', 'an', 'on', 'no', 'nad', 'red', 'added', 'walk', 'as', 'asa', 'resveratrol',
            'prednisone', 'artifact', 'four', 'hard', 'sonsor', 'enlyte', 'stevia', 'extra', 'with', 'it', '/', 'd', 'dinner',
            'tums', 'late', 'same', 'binders', 'now', 'histamine', 'headache', 'at', 'k', 'w', 'mg', 'd', '/', 'of', 'hr',
            'frig', 'frig', 'next']
    int_string = [x for x in string if x not in drop]
    string_3 = [x for x in int_string if x not in drop]
    new_string = []
    for word in int_string:
        if ',' in word:
            new_string.append(word.replace(',', ''))
        elif 'x,' in word:
            new_string.append(word.replace('x,', ''))
        elif '.' in word:
            new_string.append(word.replace('.', ''))
        elif '/' in word:
            new_string.append(word.replace('/', ''))
        else:
            new_string.append(word)
    new_string = list(set(new_string))
    for col in new_string:
        daily_notes[col] = 0
    # a = st.empty()
    # b = st.empty()
    # a.write('I am working your data...')
    for idx, r in daily_notes.iterrows():
        starting_list = daily_notes.loc[idx, 'Notes'].split(' ')
        if len(starting_list) == 1:
            pass
        else:
            working_list = [x for x in starting_list if x not in drop]
            for word in working_list:
                # b.write(idx)
                daily_notes.loc[idx, word] = 1+daily_notes.loc[idx, word]
    daily_notes.drop(['Notes', 'next'], axis=1, inplace=True)
    daily_notes = daily_notes.rename(columns={'DateTime': 'date'})
    return daily_notes


st.set_page_config(layout="wide")
a = st.empty()
a.write('I am loading your data...')
path = './most_recent_data/'
files = os.listdir(path)
#
#
# # create df
df = pd.DataFrame()
for file in files:
    # print(f'\nLoading file {file}...')
    temp = pd.read_csv(path+file, header=1, low_memory=False)
    df = df.append(temp)
    # print(f'appended {file} to df')
a.write('I am working your data...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")
df.drop(['Device', 'Serial Number',
        'Non-numeric Rapid-Acting Insulin', 'Rapid-Acting Insulin (units)',
         'Carbohydrates (grams)', 'Carbohydrates (servings)',
         'Non-numeric Long-Acting Insulin', 'Long-Acting Insulin (units)',
         'Ketone mmol/L', 'Meal Insulin (units)', 'Correction Insulin (units)',
         'User Change Insulin (units)', 'Strip Glucose mg/dL'], inplace=True, axis=1)

df1 = df.drop_duplicates()
glu_only = Combine_Glu(df1)

# st.write('df1', df1)

food_by_day = Combine_Notes(df1)
# st.write('notes only', food_by_day)


glu_by_day = Get_Glu_By_Day(glu_only)
# st.write(glu_by_day)

freestyle_by_day = pd.merge(glu_by_day, food_by_day, on='date', how='outer')
st.write(freestyle_by_day)
freestyle_by_day.to_csv('freestyle_by_day.csv', index=False)
a.write('I have finished your data and written the export file freestyle_by_day.csv')
