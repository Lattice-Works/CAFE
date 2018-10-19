from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os

def combine_physio_condition(basedir, subject, inphysio, inphysiocolumn, incat, incatcolumn):
    # read in physio
    physiofile = os.path.join(basedir,'derivatives/preprocessed',subject,'physio/%s.csv'%inphysio)
    physio = pd.read_csv(physiofile, parse_dates=['timestamp'])

    # read in categorical
    catfile = os.path.join(basedir,'derivatives/preprocessed',subject,'conditions/%s.csv'%incat)
    cat = pd.read_csv(catfile, parse_dates=['timestamp_offset', 'timestamp_onset'])

    # add condition to physio
    for idx,row in cat.iterrows():
        timepoints_in_condition = np.where((physio['timestamp'] > row['timestamp_onset']) & (physio['timestamp'] < row['timestamp_offset']))[0]
        physio.at[timepoints_in_condition,incatcolumn] = row[incatcolumn]

    # remove empty
    physio = physio.dropna(subset=[incatcolumn])
    physio['subject_ID'] = subject

    return physio[['subject_ID','timestamp',incatcolumn, inphysiocolumn]]

def combine_2_conditions(basedir, subject, cat1, cat1col, cat2, cat2col):
    # read in cat1
    cat1file = os.path.join(basedir,'derivatives/preprocessed',subject,'conditions/%s.csv'%cat1)
    cat1 = pd.read_csv(cat1file, parse_dates=['timestamp_offset', 'timestamp_onset'])

    # read in cat2
    cat2file = os.path.join(basedir,'derivatives/preprocessed',subject,'conditions/%s.csv'%cat2)
    cat2 = pd.read_csv(cat2file, parse_dates=['timestamp_offset', 'timestamp_onset'])

    # add transition variable
    cat1['transition'] = False
    cat1[cat2col] = None

    # loop over cuts and split cells in cat1 at cuts
    for idx,row in cat2.iterrows():
        cut = row['timestamp_onset']
        chcell = np.where((cut > cat1['timestamp_onset']) & (cut < cat1['timestamp_offset']))[0]
        if len(chcell)==0:
            continue
        splitrow = dict(cat1.iloc[chcell[0]])
        cat1.at[chcell[0],'timestamp_offset'] = cut
        cat1.at[chcell[0],'transition'] = True
        if not idx == 0:
            cat1.at[chcell[0],cat2col] = cat2.loc[idx-1,cat2col].replace(" ", "")
        splitrow['timestamp_onset'] = cut
        splitrow['transition'] = True
        splitrow[cat2col] = row[cat2col].replace(" ", "")
        cat1 = cat1.append(splitrow,ignore_index=True).sort_values(by='timestamp_onset').reset_index(drop=True)

    # fill table with conditions
    for idx,row in cat2.iterrows():
        condtimes = (cat1['timestamp_onset'] >= row['timestamp_onset']) & \
            (cat1['timestamp_offset'] <= row['timestamp_offset'])
        cat1.loc[condtimes,cat2col] = row[cat2col].replace(" ","")

    cat1 = cat1.dropna(subset=[cat2col])
    cat1['subject_ID'] = subject

    return cat1[['subject_ID', 'timestamp_onset', 'timestamp_offset', cat1col, cat2col, 'transition']]

def combine_2_conditions_all(basedir, cat1, cat1col, cat2, cat2col):
    # we first obtain the dataset above for all kids
    group_info_file = os.path.join(basedir,"group_information.csv")
    group_info = pd.read_csv(group_info_file,index_col="Subject ID")

    all_subjects = pd.DataFrame({})
    for subject, row in group_info.iterrows():
        subject_info_file = os.path.join(basedir,subject,"subject_information.csv")
        subject_info = pd.read_csv(subject_info_file)
        combined = combine_2_conditions(basedir, subject, cat1, cat1col, cat2, cat2col)
        all_subjects = all_subjects.append(combined, ignore_index=True)

    all_subjects['duration'] = (all_subjects['timestamp_offset'] - all_subjects['timestamp_onset']).apply(lambda x: x.total_seconds())
    return all_subjects

def add_percentage(row,times):
    time = row['sum']
    totaltime = times.loc[(row.name[0],row.name[2]),'sum']
    return time/totaltime

def group_2_conditions(all_subjects, cat1col, cat2col, includetransition):
    if not includetransition:
        data = all_subjects[all_subjects.transition==False]
        if len(data)==0:
            return pd.DataFrame({})
    else:
        data = all_subjects

    grouped = data[['subject_ID', cat1col, cat2col,'duration']].groupby(['subject_ID', cat1col, cat2col]).aggregate(['mean','count','median','sum'])
    grouped.columns = ['mean','count','median','sum']

    # add percentage per cat2col
    totaltimes = grouped[['sum']].groupby(['subject_ID',cat2col]).aggregate('sum')
    grouped['percentage'] = grouped.apply(add_percentage,args=(totaltimes,),axis=1)

    # reorder levels for easy reading
    grouped = grouped.reorder_levels(['subject_ID',cat2col,cat1col], axis=0).sort_index(level=['subject_ID',cat2col]).reset_index()
    return grouped
