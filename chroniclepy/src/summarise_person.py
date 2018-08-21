import pandas as pd
import numpy as np
import os
import re

def summarise_d(preprocessed):
    # simple daily aggregate functions

    dailyfunctions = {
        "duration_seconds": {
            "dur": 'sum'
            },
        "switch_app": {
            "appcnt": 'sum'
        }
    }

    daily = preprocessed.groupby('date').agg(dailyfunctions)
    daily.columns = daily.columns.droplevel(0)
    daily['dur'] = daily['dur']/60.
    daily.index = pd.to_datetime(daily.index)

    # fill days of no usage

    datelist = pd.date_range(start = np.min(daily.index), end = np.max(daily.index), freq='D')
    for date in datelist:
        if not date in daily.index:
            newrow = pd.Series({k:0 for k in daily.columns}, name=date)
            daily = daily.append(newrow)

    return daily

def summarise_hourly(preprocessed,datelist):

    # hourly daily aggregate functions
    hourlyfunctions = {
        "duration_seconds": {
            "dur": 'sum'
        },
        'switch_app': {
            "appcnt": "sum"
        }
    }

    hourly = preprocessed.groupby(['date','hour']).agg(hourlyfunctions)
    hourly.columns = hourly.columns.droplevel(0)
    hourly['dur'] = hourly['dur']/60.


    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            multind = (datestr,hour)
            if not multind in hourly.index:
                newrow = pd.Series({k:0 for k in hourly.columns}, name=multind)
                hourly = hourly.append(newrow)

    hourly = hourly.unstack('hour')
    hourly.columns = ["hourly_%s_h%i"%(x[0],int(x[1])) for x in hourly.columns.values]
    hourly.index = pd.to_datetime(hourly.index)

    return hourly

def summarise_quarterly(preprocessed,datelist):
    # quarterly daily aggregate functions
    quarterlyfunctions = {
        "duration_seconds": {
            "dur": 'sum'
        },
        'switch_app': {
            "appcnt": "sum"
        }
    }

    quarterly = preprocessed.groupby(['date','hour','quarter']).agg(quarterlyfunctions)
    quarterly.columns = quarterly.columns.droplevel(0)
    quarterly['dur'] = quarterly['dur']/60.

    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            for quarter in range(1,5):
                multind = (datestr,hour,quarter)
                if not multind in quarterly.index:
                    newrow = pd.Series({k:0 for k in quarterly.columns}, name=multind)
                    quarterly = quarterly.append(newrow)

    quarterly = quarterly.unstack('hour').unstack('quarter')
    quarterly.columns = ["quarterly_%s_h%i_q%i"%(x[0],int(x[1]),int(x[2])) for x in quarterly.columns.values]
    quarterly.index = pd.to_datetime(quarterly.index)
    return quarterly

def summarise_sessions(preprocessed):
    sescols = [x for x in preprocessed.columns if x.startswith('engage')]

    # session durations
    for sescol in sescols:
        newcol = '%sdur'%sescol
        sesids = np.where(preprocessed[sescol]==1)[0][1:]
        starttimes = np.array(preprocessed.start_timestamp.loc[np.append([0],sesids)][:-1])
        endtimes = np.array(preprocessed.end_timestamp.loc[sesids-1])
        durs = (endtimes-starttimes)/ np.timedelta64(1, 'm')
        preprocessed.at[(sesids-1),newcol] = durs

    # sessions
    sesfunctions = {k: 'sum' for k in sescols}
    sesfunctions.update({"%sdur"%k: 'mean' for k in sescols})
    sessions = preprocessed.groupby(['date']).agg(sesfunctions)
    sessions[sescols] = sessions[sescols].astype('int')
    sescols = sesfunctions.keys()
    sessions.columns = ["engage%s"%ses.split("_")[1] for ses in sescols]
    sessions.index = pd.to_datetime(sessions.index)

    return sessions, sescols

def summarise_recodes(preprocessed,ignorecols):
    # recoded functions

    addedcols = list(set(preprocessed.columns) - set(ignorecols))
    custom = pd.DataFrame({})

    for addedcol in addedcols:
        preprocessed[addedcol] = preprocessed[addedcol].fillna("NA")
        customgrouped = preprocessed[['date',addedcol,'duration_seconds']].groupby(['date',addedcol]).agg(sum).unstack(addedcol)
        customgrouped.columns = ["custom_%s_%s"%(addedcol,x) for x in customgrouped.columns.droplevel(0)]
        customgrouped.index = pd.to_datetime(customgrouped.index)
        if len(custom)==0:
            custom = customgrouped
        else:
            custom = pd.merge(custom,customgrouped, on='date')

        #hourly
        customgrouped = preprocessed[['date',addedcol,'duration_seconds','hour']].groupby(['date',addedcol,'hour']).agg(sum).unstack([addedcol,'hour'])
        customgrouped.columns = ["custom_hourly_%s_%s_%s"%(addedcol,x[1],"h%s"%int(x[2])) for x in customgrouped.columns]
        customgrouped.index = pd.to_datetime(customgrouped.index)
        custom = pd.merge(custom,customgrouped, on='date')

        #quarterly
        customgrouped = preprocessed[['date',addedcol,'duration_seconds','hour','quarter']].groupby(['date',addedcol,'hour','quarter']).agg(sum).unstack([addedcol,'hour','quarter'])
        customgrouped.columns = ["custom_hourly_%s_%s_%s_%s"%(addedcol,x[1],"h%i"%int(x[2]),"q%i"%int(x[3])) for x in customgrouped.columns]
        customgrouped.index = pd.to_datetime(customgrouped.index)
        custom = pd.merge(custom,customgrouped, on='date')

    return custom


def summarise_daily(preprocessed):

    stdcols = ['participant_id', 'app_fullname', 'date', 'start_timestamp',
           'end_timestamp', 'day', 'hour', 'quarter',
           'duration_seconds', 'weekdayMTh', 'weekdaySTh', 'weekdayMF', 'switch_app',
           'endtime', 'starttime']

    preprocessed.index = range(len(preprocessed))

    daily = summarise_d(preprocessed)
    datelist = pd.date_range(start = np.min(daily.index), end = np.max(daily.index), freq='D')
    hourly = summarise_hourly(preprocessed,datelist)
    daily = pd.merge(daily,hourly, on='date')
    quarterly = summarise_quarterly(preprocessed,datelist)
    daily = pd.merge(daily,quarterly, on='date')
    sessions, sescols = summarise_sessions(preprocessed)
    daily = pd.merge(daily,sessions, on='date')
    custom = summarise_recodes(preprocessed,set(stdcols).union(set(sescols)))
    daily = pd.merge(daily,custom, on='date')

    # get appsperminute
    appcnts = [x for x in daily.columns if 'appcnt' in x]
    for col in appcnts:
        daily[col.replace("appcnt","switchpermin")] = daily[col]/daily[col.replace("appcnt","dur")]
    daily = daily.drop(appcnts,axis=1)

    return daily
