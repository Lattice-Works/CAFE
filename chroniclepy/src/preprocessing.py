from datetime import datetime, timedelta
from collections import Counter
from pytz import timezone
from .utils import utils
import pandas as pd
import numpy as np
import os
import re

def read_and_clean_data(filenm):
    '''
    This function transforms a csv file into a clean dataset:
    - only move-to-foreground and move-to-background actions
    - extracts person ID
    - extracts datetime information and rounds to 10ms
    - sorts events from the same 10ms by (1) foreground, (2) background
    '''
    personid = "-".join(str(filenm).split(".")[-2].split("-")[1:])
    thisdata = pd.read_csv(filenm)
    thisdata['person'] = personid
    thisdata = thisdata.dropna(subset=['ol.recordtype','ol.datelogged'])
    if len(thisdata)==0:
        return(thisdata)
    thisdata = thisdata[thisdata['ol.recordtype'] != 'Usage Stat']
    thisdata = thisdata[['general.fullname','ol.recordtype','ol.datelogged','person']]
    thisdata['dt_logged'] = thisdata.apply(utils.get_dt,axis=1)
    thisdata['action'] = thisdata.apply(utils.get_action,axis=1)
    thisdata = thisdata.sort_values(by=['dt_logged','action']).reset_index(drop=True)
    return thisdata.drop(['action'],axis=1)

def get_timestamps(prevtime,curtime,row=None,precision=60):
    '''
    Function transforms an app usage statistic into bins (according to the desired precision).
    Returns a dataframe with the number of rows the number of time units (= precision).
    Precision in seconds.
    '''
    # round down to precision
    prevtimehour = prevtime.replace(microsecond=0,second=0,minute=0)
    seconds_since_prevtimehour = np.floor((prevtime-prevtimehour).seconds/precision)*precision
    prevtimerounded = prevtimehour+timedelta(seconds=seconds_since_prevtimehour)

    # number of timepoints on precision scale (= new rows )
    timedif = (curtime-prevtimerounded)
    timepoints_n = int(np.floor(timedif.seconds/precision)+int(timedif.days*24*60*60/precision))

    # run over timepoints and append datetimestamps
    delta = timedelta(seconds=0)
    outtime = []
    for timepoint in range(timepoints_n+1):
        starttime = prevtime if timepoint == 0 else prevtimerounded+delta
        endtime = curtime if timepoint == timepoints_n else prevtimerounded+delta+timedelta(seconds=precision)
        outmetrics = {
            "start_timestamp": starttime,
            "end_timestamp": endtime,
            "date": starttime.strftime("%Y-%m-%d"),
            "day": starttime.weekday(),
            "weekday": 0 if starttime.weekday() < 5 else 1,
            "hour": starttime.hour,
            "quarter": int(np.floor(starttime.minute/15.)*15),
            "duration_seconds": (endtime-starttime).seconds,
        }

        outmetrics['participant_id'] = row['person']
        outmetrics['app_fullname'] = row['general.fullname']

        delta = delta+timedelta(seconds=precision)
        outtime.append(outmetrics)

    return pd.DataFrame(outtime)

def extract_usage(filename,precision=3600,recode=None):
    '''
    function to extract usage from a filename.  Precision in seconds.
    '''

    cols = ['participant_id',
            'app_fullname',
            'date',
            'start_timestamp',
            'end_timestamp',
            'day', # note: starts on Monday !
            'weekday',
            'hour',
            'quarter',
            'duration_seconds']

    alldata = pd.DataFrame()
    rawdata = read_and_clean_data(filename)
    openapps = {}

    for idx, row in rawdata.iterrows():

        interaction = row['ol.recordtype']
        app = row['general.fullname']

        # decode timestamp and correct for timezone
        curtime = row.dt_logged

        if interaction == 'Move to Foreground':
            openapps[app] = {"open" : True,
                             "time": curtime}

        if interaction == 'Move to Background':

            if app in openapps.keys() and openapps[app]['open']==True:

                # get time of opening
                prevtime = openapps[app]['time']

                if curtime-prevtime<timedelta(0):
                    raise ValueError("ALARM ALARM: timepoints out of order !!")

                # split up timepoints by precision
                timepoints = get_timestamps(prevtime,curtime,precision=precision,row=row)

                alldata = pd.concat([alldata,timepoints])


            openapps[app] = {"open": False}

    if len(alldata)>0:
        alldata = alldata.sort_values(by=['start_timestamp','end_timestamp'])
        if isinstance(recode,pd.DataFrame):
            alldata[recode.columns] = alldata.reset_index(drop=True).apply(lambda x: utils.recode(x,recode),axis=1)
        return alldata[cols+list(recode.columns)].reset_index(drop=True)


def check_overlap_add_sessions(data, session_def = 5*60):
    '''
    Function to loop over dataset, spot overlaps (and remove them), and add columns
    to indicate whether a new session has been started or not.
    '''
    data = data[data.duration_seconds > 0].reset_index(drop=True)

    # initiate session column(s)
    if isinstance(session_def,int):
        data['newsession'] = False
    elif isinstance(session_def,list):
        for sess in session_def:
            data['newsession_%is'%int(sess)] = False
    else:
        raise ValueError("ERROR: I don't understand the type of the session definition.")

    # loop over dataset:
    # - prevent overlap (with warning)
    # - check if a new session is started
    for idx,row in data.iterrows():
        if idx == 0:
            continue

        # check overlap
        nousetime = row['start_timestamp']-data['end_timestamp'].iloc[idx-1]
        if nousetime < timedelta(microseconds=0):
            print("WARNING: Overlapping usage for participant %s: %s was open since %s when %s was openened on %s. \
            Manually closing %s..."%(
                row['participant_id'],
                data.iloc[idx-1]['app_fullname'],
                data.iloc[idx-1]['start_timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                row['app_fullname'],
                row['start_timestamp'].strftime("%Y-%m-%d %H:%M:%S"),
                data.iloc[idx-1]['app_fullname']
            ))
            data.at[idx-1,'end_timestamp'] = row['start_timestamp']
            data.at[idx-1,'duration_seconds'] = (data.at[idx-1,'end_timestamp']-data.at[idx-1,'start_timestamp']).seconds
        # check sessions
        else:
            if isinstance(session_def,int):
                if nousetime > timedelta(seconds = session_def):
                    data.at[idx, 'newsession'] = True
            else:
                for sess in session_def:
                    if nousetime > timedelta(seconds = sess):
                        data.at[idx, 'newsession_%is'%int(sess)] = True

    return data.reset_index(drop=True)

def preprocess(infolder,outfolder,recodefile=None,precision=3600,sessioninterval = 5*60):
    if isinstance(recodefile,str):
        recode = pd.read_csv("utils/data/appcat.csv",index_col='fullname')
    else:
        recode = None

    for filename in os.listdir(infolder):
        tmp = extract_usage(os.path.join(infolder,filename),precision=precision,recode=recode)
        if not isinstance(tmp,pd.DataFrame):
            print("WARNING: File %s does not seem to contain relevant data.  Skipping..."%filename)
            continue
        data = check_overlap_add_sessions(tmp,session_def=sessioninterval)
        data.to_csv(os.path.join(outfolder,filename))
