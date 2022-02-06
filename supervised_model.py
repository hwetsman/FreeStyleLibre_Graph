#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sunday Feb 06 2022

@author: howardwetsman
To do: import data
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


# get most recent data
path = './most_recent_data/'
# files = os.listdir(path)
file = os.listdir(path)[0]
# create df
df = pd.read_csv(path+file, header=1)

# convert timestamps to datetime
print('\nConverting Timestamps...')
df['Device Timestamp'] = pd.to_datetime(df['Device Timestamp'], format="%m-%d-%Y %I:%M %p")
