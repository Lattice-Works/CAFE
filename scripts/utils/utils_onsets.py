from datetime import datetime, timedelta
from collections import Counter
import pandas as pd
import numpy as np
import os

def extract_onsets(all_subjects, cat1, cat1col, cat2, cat2col, cat2val):
    onsettable = pd.DataFrame({})
    for index,event in all_subjects.iterrows():
        subid = all_subjects.loc[index,'subject_ID']
        subsubset = all_subjects[all_subjects.subject_ID==subid]
        firstsubidx = np.where(subsubset['timestamp_onset']==max(subsubset['timestamp_onset']))[0][0]
        pdid_first = subsubset.iloc[firstsubidx].name
        lastsubidx = np.where(subsubset['timestamp_onset']==max(subsubset['timestamp_onset']))[0][0]
        pdid_last = subsubset.iloc[lastsubidx].name

        # verify if we're talking about the onset of cat1col
        if (not index==0):
            if (event[cat1col] == all_subjects.loc[index-1,cat1col]) and (event['subject_ID'] == all_subjects.loc[index-1,'subject_ID']):
                continue

        # look at past
        # these are not by def instantiated
        inprog_sec = None
        nexttime_sec = None
        mainta_sec = None

        if index == 0:
            lasttime_sec = None

        for idx in range(index)[::-1]:
            # if event ongoing: since when
            if event[cat2col] == cat2val:
                if not all_subjects.loc[idx,cat2col] == cat2val or \
                not all_subjects.loc[idx,'subject_ID'] == subid:
                    ongoingsince = all_subjects.loc[idx+1,'timestamp_onset']
                    inprog = event['timestamp_onset']-ongoingsince
                    inprog_sec = inprog.seconds+inprog.microseconds/10**6
                    lasttime_sec = None
                    break

            # if event not oingoing: when was last time (seconds last offset to current onset)
            else:
                if all_subjects.loc[idx,'subject_ID'] != subid:
                    lasttime_sec = None
                    break
                if all_subjects.loc[idx,cat2col] == cat2val:
                    lasttime = event['timestamp_onset']-all_subjects.loc[idx,'timestamp_offset']
                    lasttime_sec = lasttime.seconds + lasttime.microseconds/10**6
                    break

        # look into future
        for idx in range(index,len(all_subjects)):
            # if event is ongoing: until when?
            if event[cat2col] == cat2val:
                if not all_subjects.loc[idx,cat2col] == cat2val or \
                not all_subjects.loc[idx,'subject_ID'] == subid:
                    ongoinguntil = all_subjects.loc[idx-1,'timestamp_offset']
                    mainta = ongoinguntil-event['timestamp_onset']
                    mainta_sec = mainta.seconds+mainta.microseconds/10**6
                    nexttime_sec = None
                    break
            # if not, when is the next time (seconds current onset to next onset)
            else:
                if all_subjects.loc[idx,cat2col] == cat2val:
                    nexttime = all_subjects.loc[idx,'timestamp_onset'] - event['timestamp_onset']
                    nexttime_sec = nexttime.seconds + nexttime.microseconds/10**6
                    break
                if all_subjects.loc[idx,'subject_ID'] != subid:
                    nexttime_sec = None
                    break


        fullblock = all_subjects[(all_subjects[cat1col]==event[cat1col]) & (all_subjects['subject_ID']==event['subject_ID'])]
        ons = fullblock.iloc[0]['timestamp_onset']
        off = fullblock.iloc[len(fullblock)-1]['timestamp_offset']
        duration = off - ons
        duration_sec = duration.seconds + duration.microseconds/10**6

        counts = dict(Counter(fullblock[cat2col]))
        entire = True
        if len(counts.keys()) == 1 and cat2val in counts.keys():
            entire = True
            percentage = 1.
        else:
            entire = False
            percentage = np.sum(fullblock.duration[fullblock[cat2col] == cat2val]) / np.sum(fullblock.duration)

        newrow = {
            "subject_ID": event['subject_ID'],
            "%s_ID"%cat1: event[cat1col],
            "%s_onset"%cat1: event['timestamp_onset'],
            "%s_duration"%cat1: duration_sec,
            "%s-%s_at_onset"%(cat2,cat2val): event[cat2col] == cat2val,
            "onset_%s-%s_time_in_progress"%(cat2,cat2val): inprog_sec,
            "onset_%s-%s_time_maintained"%(cat2,cat2val): mainta_sec,
            "onset_%s-%s_time_since_last"%(cat2,cat2val): lasttime_sec,
            "onset_%s-%s_time_until_next"%(cat2,cat2val): nexttime_sec,
            "%s_entire"%cat2: entire,
            "%s_percentage"%cat2: percentage
        }
        onsettable = onsettable.append(newrow,ignore_index=True)
    return onsettable
