import pandas as pd
import numpy as np
import os
import re


def summarise_daily(preprocessed):
    stdcols = ['participant_id', 'app_fullname', 'date', 'start_timestamp',
           'end_timestamp', 'day', 'hour', 'quarter',
           'duration_seconds', 'weekdayMTh', 'weekdaySTh', 'weekdayMF', 'switch_app',
           'endtime', 'starttime']

    sescols = [x for x in preprocessed.columns if x.startswith('new_engage')]

    # simple daily aggregate functions

    dailyfunctions = {
        "duration_seconds": {
            "duration": 'sum'
            },
        "switch_app": {
            "appcnt": 'sum'
        }
    }

    daily = preprocessed.groupby('date').agg(dailyfunctions)
    daily.columns = daily.columns.droplevel(0)
    daily['duration'] = daily['duration']/60.
    daily.index = pd.to_datetime(daily.index)

    # fill days of no usage

    datelist = pd.date_range(start = np.min(daily.index), end = np.max(daily.index), freq='D')
    for date in datelist:
        if not date in daily.index:
            newrow = pd.Series({k:0 for k in daily.columns}, name=date)
            daily = daily.append(newrow)

    # hourly daily aggregate functions

    hourlyfunctions = {
        "duration_seconds": {
            "duration": 'sum'
        },
        'switch_app': {
            "appcnt": "sum"
        }
    }

    hourly = preprocessed.groupby(['date','hour']).agg(hourlyfunctions)
    hourly.columns = hourly.columns.droplevel(0)
    hourly['duration'] = hourly['duration']/60.

    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            multind = (datestr,hour)
            if not multind in hourly.index:
                newrow = pd.Series({k:0 for k in hourly.columns}, name=multind)
                hourly = hourly.append(newrow)

    hourly = hourly.unstack('hour')
    hourly.columns = ["hourly_%s_h%s"%(x[0],x[1]) for x in hourly.columns.values]
    hourly.index = pd.to_datetime(hourly.index)

    daily = pd.merge(daily,hourly, on='date')

    # sessions

    sesfunctions = {k: 'sum' for k in sescols}

    sessions = preprocessed.groupby(['date']).agg(sesfunctions)
    sessions.columns = ["engage_%s"%ses.split("_")[2] for ses in (sessions.columns)]
    sessions = sessions.astype('int')
    sessions.index = pd.to_datetime(sessions.index)

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
