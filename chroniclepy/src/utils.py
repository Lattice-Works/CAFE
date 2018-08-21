from datetime import datetime, timedelta, timezone
from collections import Counter
import pandas as pd
import numpy as np
import pytz
import os
import re

def get_dt(row):
    '''
    This function transforms the reported (string) datetime to a timestamp.
    A few notes:
    - Time is rounded to 10 milliseconds, to make sure the apps are in the right order.
      A potential downside of this is that when a person closes and re-opens an app
      within 10 milliseconds, it will be regarded as closed.
    '''

    zulutime = row['ol.datelogged'].split("Z")[0]
    try:
        zulutime = datetime.strptime(zulutime,"%Y-%m-%dT%H:%M:%S.%f")
    except ValueError:
        zulutime = datetime.strptime(zulutime,"%Y-%m-%dT%H:%M:%S")
    localtime = zulutime.replace(tzinfo=timezone.utc).astimezone(tz=pytz.timezone(row['ol.timezone']))
    return localtime

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

def logger(message,level=1):
    time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    prefix = "༼ つ ◕_◕ ༽つ" if level==0 else "-- "
    print("%s %s: %s"%(prefix,time,message))
