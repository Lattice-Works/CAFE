from chroniclepy import utils, summarise_person
from datetime import datetime, timedelta
from collections import Counter
from pytz import timezone
import pandas as pd
import numpy as np
import os
import re

def summary(infolder, outfolder, includestartend=False, recodefile=None, quarterly = False):

    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    files = [x for x in os.listdir(infolder) if x.startswith("Chronicle")]

    alldata = pd.DataFrame({})
    for filenm in files:
        utils.logger("LOG: Summarising file %s..."%filenm,level=1)
        personid = "-".join(str(filenm).split(".")[-2].split("-")[1:])
        preprocessed = pd.read_csv(os.path.join(infolder,filenm), index_col=0, parse_dates = ['start_timestamp','end_timestamp'])
        if isinstance(recodefile,str):
            recode = pd.read_csv(recodefile,index_col='full_name').astype(str)
            newcols = preprocessed.apply(lambda x: utils.recode(x,recode),axis=1)
            preprocessed[recode.columns] = newcols
        if not includestartend:
            preprocessed = preprocessed[
                (preprocessed['start_timestamp'].dt.date!= min(preprocessed['start_timestamp']).date()) & \
                (preprocessed['start_timestamp'].dt.date!= max(preprocessed['start_timestamp']).date())]
        daily = summarise_person.summarise_daily(preprocessed,quarterly = True)
        daily['participant_id'] = personid
        daily = daily.fillna(0)
        alldata = pd.concat([alldata,daily])

    summary = alldata.groupby('participant_id').agg(['mean','std'])
    summary.columns = ["%s_%s"%(x[0],x[1]) for x in summary.columns]
    summary['num_days'] = alldata[['dur','participant_id']].groupby('participant_id').agg(['count'])

    customcols = [x for x in summary.columns if x.startswith("custom") and not 'hourly' in x and not 'quarterly' in x]
    hourlycols = [x for x in summary.columns if 'hourly' in x]
    quarterlycols = [x for x in summary.columns if 'quarterly' in x]
    othercols = [x for x in summary.columns if not (x.startswith("hourly") or x.startswith("custom") or x.startswith("quarterly"))]

    # # rename columns
    daily = summary[othercols+customcols] \
        .rename(columns = {k:k.replace("custom_","") for k in customcols})

    hourly = summary[hourlycols] \
        .drop([x for x in hourlycols if x.endswith('std')],axis=1) \
        .rename(columns = {k:k.replace("custom_","").replace("hourly_","") for k in hourlycols})

    quarterly = summary[quarterlycols] \
        .drop([x for x in quarterlycols if x.endswith('std')],axis=1) \
        .rename(columns = {k:k.replace("custom_","").replace("quarterly_","") for k in quarterlycols})

    custom = summary[customcols] \
        .rename(columns = {k:k.replace("custom_","") for k in customcols})

    daily.to_csv(os.path.join(outfolder,'summary_daily.csv'))
    hourly.to_csv(os.path.join(outfolder,'summary_hourly.csv'))
    quarterly.to_csv(os.path.join(outfolder,'summary_quarterly.csv'))
    custom.to_csv(os.path.join(outfolder,'summary_appcoding.csv'))
