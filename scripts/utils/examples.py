from utils import utils_combine
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import os

basedir = "/Users/jokedurnez/Desktop/Heather Info for CAFE Physio Pilot/Preliminary Physio Wristband Data for Mollie/data/"

# here we combine a physio dataset with a categorical variable.  The specific columns is also specified to combine the
# two datasets.
inphysio = 'ACC'
inphysiocolumn = 'SVM'
incat = 'TV'
incatcolumn = 'code'
subject = 'WI_AMP_005'

physiocombined = utils_combine.combine_physio_condition(basedir, subject, inphysio, inphysiocolumn, incat, incatcolumn)

# we combine two categorical datasets (eg. TV and attention).
cat2 = 'TV'
cat2col = 'code'
cat1 = 'attention'
cat1col = 'codegeneralised'
subject = 'WI_AMP_021'
includetransition = False

catcombined = utils_combine.combine_2_conditions(basedir, subject, cat1, cat1col, cat2, cat2col)

#####################
# Next we make a proof-of-concept on how to easily use the combined datasets to compute summary statistics.
# at this point, we cannot yet take specific values for the condition (eg. toys in attention), but this will
# be included together with the other summary streams.
#####################

# we first obtain the dataset above for all kids
group_info_file = os.path.join(basedir,"group_information.csv")
group_info = pd.read_csv(group_info_file,index_col="Subject ID")

all_subjects = pd.DataFrame({})
for subject, row in group_info.iterrows():
    combined = utils_combine.combine_2_conditions(basedir, subject, cat1, cat1col, cat2, cat2col)
    all_subjects = all_subjects.append(combined, ignore_index=True)

all_subjects['duration'] = (all_subjects['timestamp_offset'] - all_subjects['timestamp_onset']).apply(lambda x: x.total_seconds())

outsummary = os.path.join(basedir,'derivatives/summary')
if not os.path.exists(outsummary):
    os.mkdir(outsummary)

######### GROUP ALL

# Here we group the duration by subjectID, TV.code and attention.codegeneralised (without suffix)
grouped = all_subjects[['subject_ID', cat1col, cat2col,'duration']].groupby(['subject_ID', cat1col, cat2col]).aggregate(['mean','count','median','sum'])
grouped.columns = ['mean','count','median','sum']

# add percentage per cat2col
totaltimes = grouped[['sum']].groupby(['subject_ID',cat2col]).aggregate('sum')
def add_percentage(row):
    time = row['sum']
    totaltime = totaltimes.loc[(row.name[0],row.name[2]),'sum']
    return time/totaltime
grouped['percentage'] = grouped.apply(add_percentage,axis=1)

# reorder levels for easy reading
grouped = grouped.reorder_levels(['subject_ID','code','codegeneralised'], axis=0).sort_index(level=['subject_ID','code']).reset_index()
grouped.to_csv(os.path.join(outsummary,"summary_%s-%s_%s-%s.csv"%(cat1,cat1col,cat2,cat2col)))

######### GROUP TRIMMED

grouped = all_subjects[all_subjects.transition==False][['subject_ID', cat1col, cat2col,'duration']].groupby(['subject_ID', cat1col, cat2col]).aggregate(['mean','count','median','sum'])
grouped.columns = ['mean','count','median','sum']

# add percentage per cat2col
totaltimes = grouped[['sum']].groupby(['subject_ID',cat2col]).aggregate('sum')
def add_percentage(row):
    time = row['sum']
    totaltime = totaltimes.loc[(row.name[0],row.name[2]),'sum']
    return time/totaltime
grouped['percentage'] = grouped.apply(add_percentage,axis=1)

# reorder levels for easy reading
grouped = grouped.reorder_levels(['subject_ID','code','codegeneralised'], axis=0).sort_index(level=['subject_ID','code']).reset_index()
grouped.to_csv(os.path.join(outsummary,"summary_%s-%s_%s-%s_trimmed.csv"%(cat1,cat1col,cat2,cat2col)))

######### GROUP PHYSIO
variable_of_interest = {
    "ACC": "SVM",
    "EDA": "EDA_0",
    "BVP": "BVP_0",
    "TEMP": "TEMP_0",
    "HR": "HR_0",
    "IBI": "IBI"
}

physio = pd.DataFrame({})
for subject, row in group_info.iterrows():
    for inphysio, inphysiocolumn in variable_of_interest.items():
        incat = 'TV'
        incatcolumn = 'code'
        physiocombined = utils_combine.combine_physio_condition(basedir, subject, inphysio, inphysiocolumn, incat, incatcolumn)
        grouped = physiocombined.groupby([incatcolumn,'subject_ID']).aggregate(['mean','count','median','sum'])
        grouped.columns = ['mean','count','median','sum']
        grouped['metric'] = inphysio
        physio = physio.append(grouped.reset_index(),ignore_index=True)

physio.to_csv(os.path.join(outsummary,"summary_physio_%s-%s.csv"%(incat, incatcolumn)))
