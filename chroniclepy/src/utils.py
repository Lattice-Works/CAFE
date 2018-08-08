from datetime import datetime, timedelta
from collections import Counter
from pytz import timezone
import pandas as pd
import numpy as np
import os
import re

def get_dt(row):
    '''
    This function transforms the reported (string) datetime to a timestamp.
    A few notes:
    - THIS DOES NOT TAKE INTO ACCOUNT TIMEZONE ! This is for a previous version of
      chronicle that didn't save time zone information yet.
    - Time is rounded to 10 milliseconds, to make sure the apps are in the right order.
      A potential downside of this is that when a person closes and re-opens an app
      within 10 milliseconds, it will be regarded as closed.
    '''

    datesplitted = row['ol.datelogged'].split(".")
    if len(datesplitted) > 1:
        ind = 20+len(datesplitted[1].replace("-","+").replace("Z","+").split("+")[0])
        date = datetime.strptime(row['ol.datelogged'][:ind],"%Y-%m-%dT%H:%M:%S.%f")
    else:
        ind = 19
        date = datetime.strptime(row['ol.datelogged'][:ind],"%Y-%m-%dT%H:%M:%S")
    date = date.replace(microsecond= int(np.floor(date.microsecond/100000)*100000)) #rounding to 0.01s
    if row['ol.datelogged'][24:] in ['0000',':00']:
        return date - timedelta(hours = 6)
    else:
        return date

def get_action(row):
    '''
    This function creates a column with a value 0 for foreground action, 1 for background
    action.  This can be used for sorting (when times are equal: foreground before background)
    '''
    if row['ol.recordtype']=='Move to Foreground':
        return 0
    if row['ol.recordtype']=='Move to Background':
        return 1

def recode(row,recode):
    newcols = {x:None for x in recode.columns}
    if row['app_fullname'] in recode.index:
        for col in recode.columns:
            newcols[col] = recode[col][row['app_fullname']]

    return pd.Series(newcols)
