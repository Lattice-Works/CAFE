import pandas as pd
import numpy as np
import os
import re


def summarise_daily(preprocessed):
    stdcols = ['participant_id', 'app_fullname', 'date', 'start_timestamp',
           'end_timestamp', 'day', 'weekday', 'hour', 'quarter',
           'duration_seconds']

    sescols = [x for x in preprocessed.columns if x.startswith('new_engage')]

    # simple daily aggregate functions

    dailyfunctions = {
        "duration_seconds": {
            "duration": 'sum'
            },
        "app_fullname": {
            "appcnt": 'count'
        }
    }

    daily = preprocessed.groupby('date').agg(dailyfunctions)
    daily.columns = daily.columns.droplevel(0)

    # hourly daily aggregate functions

    hourlyfunctions = {
        "duration_seconds": {
            "duration": 'sum'
        },
        'app_fullname': {
            "appcnt": "count"
        }
    }

    hourly = preprocessed.groupby(['date','hour']).agg(hourlyfunctions).unstack('hour')
    hourly.columns = ["hourly_%s_h%s"%(x[1],x[2]) for x in hourly.columns.values]

    daily = pd.merge(daily,hourly, on='date')

    # sessions

    sesfunctions = {k: 'sum' for k in sescols}

    sessions = preprocessed.groupby(['date']).agg(sesfunctions)
    sessions.columns = ["engage_%s"%ses.split("_")[2] for ses in (sessions.columns)]

    daily = pd.merge(daily,sessions, on='date')

    # recoded functions

    addedcols = list(set(preprocessed.columns) - set(stdcols) - set(sescols))

    for addedcol in addedcols:
        preprocessed[addedcol] = preprocessed[addedcol].fillna("notcoded")
        customgrouped = preprocessed[['date',addedcol,'duration_seconds']].groupby(['date',addedcol]).agg(sum).unstack(addedcol)
        customgrouped.columns = ["custom_%s_%s"%(addedcol,x) for x in customgrouped.columns.droplevel(0)]
        daily = pd.merge(daily,customgrouped, on='date')

        #hourly
        customgrouped = preprocessed[['date',addedcol,'duration_seconds','hour']].groupby(['date',addedcol,'hour']).agg(sum).unstack([addedcol,'hour'])
        customgrouped.columns = ["custom_hourly_%s_%s_%s"%(addedcol,x[1],"h%s"%x[2]) for x in customgrouped.columns]
        daily = pd.merge(daily,customgrouped, on='date')

    # get appsperminute

    appcnts = [x for x in daily.columns if 'appcnt' in x]
    for col in appcnts:
        daily[col.replace("appcnt","appswitching_per_minute")] = daily[col]/daily[col.replace("appcnt","duration")]*60.
    daily = daily.drop(appcnts,axis=1)

    return daily
