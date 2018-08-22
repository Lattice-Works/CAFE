from collections import Counter
from chroniclepy import utils
import pandas as pd
import numpy as np
import os
import re

def fill_hours(dataset,datelist):
    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            multind = (datestr,hour)
            if not multind in dataset.index:
                newrow = pd.Series({k:0 for k in dataset.columns}, name=multind)
                dataset = dataset.append(newrow)
    return dataset

def fill_quarters(dataset,datelist):
    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            for quarter in range(1,5):
                multind = (datestr,hour,quarter)
                if not multind in dataset.index:
                    newrow = pd.Series({k:0 for k in dataset.columns}, name=multind)
                    dataset = dataset.append(newrow)
    return dataset

def fill_appcat_hourly(dataset,datelist,catlist):
    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            for cat in catlist:
                multind = (datestr,str(cat),hour)
                if not multind in dataset.index:
                    newrow = pd.Series({k:0 for k in dataset.columns}, name=multind)
                    dataset = dataset.append(newrow)
    return dataset

def fill_appcat_quarterly(dataset,datelist,catlist):
    for date in datelist:
        datestr = date.strftime("%Y-%m-%d")
        for hour in range(24):
            for quarter in range(1,5):
                for cat in catlist:
                    multind = (datestr,str(cat),hour,quarter)
                    if not multind in dataset.index:
                        newrow = pd.Series({k:0 for k in dataset.columns}, name=multind)
                        dataset = dataset.append(newrow)
    return dataset

def summarise_d(preprocessed):
    # simple daily aggregate functions

    dailyfunctions = {"duration_seconds": {"dur": 'sum'},
        "switch_app": {"appcnt": 'sum'}
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

def summarise_hourly(preprocessed,datelist,engagecols):

    # hourly daily aggregate functions
    hourlyfunctions = {
        "duration_seconds": {"dur": 'sum'},
        'switch_app': {"appcnt": "sum"}
    }

    hourlyengagefunctions = {k: {"%s_num"%k: 'sum'} for k in engagecols}

    hourlyfunctions.update(hourlyengagefunctions)

    hourly = preprocessed.groupby(['date','hour']).agg(hourlyfunctions)
    hourly.columns = hourly.columns.droplevel(0)
    hourly['dur'] = hourly['dur']/60.

    hourly = fill_hours(hourly,datelist)

    hourly = hourly.unstack('hour')
    hourly.columns = ["hourly_%s_h%i"%(x[0],int(x[1])) for x in hourly.columns.values]
    hourly.index = pd.to_datetime(hourly.index)

    return hourly

def summarise_quarterly(preprocessed,datelist,engagecols):
    # quarterly daily aggregate functions
    quarterlyfunctions = {
        "duration_seconds": {"dur": 'sum'},
        'switch_app': {"appcnt": "sum"}
    }
    quarterlyengagefunctions = {k: {"%s_num"%k: 'sum'} for k in engagecols}
    quarterlyfunctions.update(quarterlyengagefunctions)
    quarterly = preprocessed.groupby(['date','hour','quarter']).agg(quarterlyfunctions)
    quarterly.columns = quarterly.columns.droplevel(0)
    quarterly['dur'] = quarterly['dur']/60.
    quarterly = fill_quarters(quarterly,datelist)
    quarterly = quarterly.unstack('hour').unstack('quarter')
    quarterly.columns = ["quarterly_%s_h%i_q%i"%(x[0],int(x[1]),int(x[2])) for x in quarterly.columns.values]
    quarterly.index = pd.to_datetime(quarterly.index)
    return quarterly

def summarise_sessions(preprocessed):
    sescols = [x for x in preprocessed.columns if x.startswith('engage')]

    # session durations
    for sescol in sescols:
        newcol = '%s_dur'%sescol
        sesids = np.where(preprocessed[sescol]==1)[0][1:]
        starttimes = np.array(preprocessed.start_timestamp.loc[np.append([0],sesids)][:-1])
        endtimes = np.array(preprocessed.end_timestamp.loc[sesids-1])
        durs = (endtimes-starttimes)/ np.timedelta64(1, 'm')
        preprocessed.at[(sesids-1),newcol] = durs

    preprocessed = preprocessed.rename(columns={sescol:"%s_cnt"%sescol for sescol in sescols})

    # sessions
    sesfunctions = {"%s_cnt"%k: 'sum' for k in sescols}
    sesfunctions.update({"%s_dur"%k: 'mean' for k in sescols})
    sessions = preprocessed.groupby(['date']).agg(sesfunctions)
    cntcols = [x for x in preprocessed.columns if x.startswith('engage') and x.endswith("cnt")]
    sessions[cntcols] = sessions[cntcols].astype('int')
    sessions.columns = sesfunctions.keys()
    sessions.index = pd.to_datetime(sessions.index)

    return sessions

def summarise_recodes(preprocessed,ignorecols,datelist,quarterly=False):
    # recoded functions
    ignore_engage = [x for x in preprocessed.columns if 'engage' in x]
    addedcols = list(set(preprocessed.columns) - set(ignorecols) - set(ignore_engage))
    custom = pd.DataFrame({})

    for addedcol in addedcols:

        preprocessed[addedcol] = preprocessed[addedcol].fillna("NA")
        catlist = list(Counter(preprocessed[addedcol]).keys())
        customgrouped = preprocessed[['date',addedcol,'duration_seconds']].groupby(['date',addedcol]).agg(sum).unstack(addedcol)
        customgrouped.columns = ["custom_%s_%s_dur"%(addedcol,x) for x in customgrouped.columns.droplevel(0)]
        customgrouped.index = pd.to_datetime(customgrouped.index)
        if len(custom)==0:
            custom = customgrouped
        else:
            custom = pd.merge(custom,customgrouped, on='date')

        #hourly
        customgrouped = preprocessed[['date',addedcol,'duration_seconds','hour']].groupby(['date',addedcol,'hour']).agg(sum)
        customgrouped = fill_appcat_hourly(customgrouped,datelist,catlist).unstack([addedcol,'hour'])
        customgrouped.columns = ["custom_hourly_%s_%s_dur_h%i"%(addedcol,x[1],int(x[2])) for x in customgrouped.columns]
        customgrouped.index = pd.to_datetime(customgrouped.index)
        custom = pd.merge(custom,customgrouped, on='date')

        #quarterly
        if quarterly:
            customgrouped = preprocessed[['date',addedcol,'duration_seconds','hour','quarter']].groupby(['date',addedcol,'hour','quarter']).agg(sum)
            customgrouped = fill_appcat_quarterly(customgrouped,datelist,catlist).unstack([addedcol,'hour','quarter'])
            customgrouped.columns = ["custom_quarterly_%s_%s_dur_h%i_q%i"%(addedcol,x[1],int(x[2]),int(x[3])) for x in customgrouped.columns]
            customgrouped.index = pd.to_datetime(customgrouped.index)
            custom = pd.merge(custom,customgrouped, on='date')

    return custom


def summarise_daily(preprocessed,quarterly=False, splitweek = True, weekdefinition = 'weekdayMF'):

    # set index
    personID = Counter(preprocessed.index).most_common(1)[0][0]
    preprocessed.index = range(len(preprocessed))

    # split columns and get recode columns
    stdcols = ['participant_id', 'app_fullname', 'date', 'start_timestamp',
           'end_timestamp', 'day', 'hour', 'quarter',
           'duration_seconds', 'weekdayMTh', 'weekdaySTh', 'weekdayMF', 'switch_app',
           'endtime', 'starttime']
    engagecols = [x for x in preprocessed.columns if x.startswith('engage')]
    noncustom = set(stdcols).union(set(engagecols))

    # check splitweek settings
    if isinstance(weekdefinition,str):
        if weekdefinition not in ['weekdayMTh', 'weekdaySTh', 'weekdayMF']:
            raise ValueError("Unknown weekday definition !")
    if splitweek and not isinstance(weekdefinition,str):
        raise ValueError("Please specify the weekdefinition if you want  !")

    daily = summarise_d(preprocessed)
    datelist = pd.date_range(start = np.min(daily.index), end = np.max(daily.index), freq='D')

    custom = summarise_recodes(preprocessed,noncustom,datelist,quarterly=quarterly)
    daily = pd.merge(daily,custom, on='date')

    hourly = summarise_hourly(preprocessed,datelist,engagecols)
    daily = pd.merge(daily,hourly, on='date')
    if quarterly:
        quarterly = summarise_quarterly(preprocessed,datelist,engagecols)
        print(len(quarterly.columns))
        daily = pd.merge(daily,quarterly, on='date')

    if splitweek:
        if np.sum(preprocessed[weekdefinition]==1)==0:
            utils.logger("WARNING: No weekday data for %s..."%personID,level=1)
        else:
            week = summarise_d(preprocessed[preprocessed[weekdefinition]==1])
            week.columns = ['week_%s'%x for x in week.columns]
            daily = pd.merge(daily,week, on='date')
        if np.sum(preprocessed[weekdefinition]==0)==0:
            utils.logger("WARNING: No weekend data for %s..."%personID,level=1)
        else:
            weekend = summarise_d(preprocessed[preprocessed[weekdefinition]==0])
            weekend.columns = ['weekend_%s'%x for x in weekend.columns]
            daily = pd.merge(daily,weekend, on='date')

    sessions = summarise_sessions(preprocessed)
    daily = pd.merge(daily,sessions, on='date')

    # get appsperminute
    appcnts = [x for x in daily.columns if 'appcnt' in x]
    for col in appcnts:
        daily[col.replace("appcnt","switchpermin")] = daily[col]/daily[col.replace("appcnt","dur")]
    daily = daily.drop(appcnts,axis=1)

    return daily
