from datetime import datetime, timedelta
from collections import Counter
from pytz import timezone
from chroniclepy import utils, summarise_person
import pandas as pd
import numpy as np
import os
import re

def summary(infolder, outfolder, includestartend=False, recodefile=None):

    if isinstance(recodefile,str):
        recode = pd.read_csv(recodefile,index_col='fullname')
        newcols = alldata.apply(lambda x: utils.recode(x,),axis=1)
        alldata[recode.columns] = newcols
        cols = cols+list(recode.columns)

    if not os.path.exists(outfolder):
        os.mkdir(outfolder)

    files = [x for x in os.listdir(infolder) if x.startswith("Chronicle")]

    alldata = pd.DataFrame({})
    for filenm in files:
        utils.logger("LOG: Summarising file %s..."%filenm,level=1)
        personid = "-".join(str(filenm).split(".")[-2].split("-")[1:])
        preprocessed = pd.read_csv(os.path.join(infolder,filenm), index_col=0, parse_dates = ['start_timestamp','end_timestamp'])
        if not includestartend:
            preprocessed = preprocessed[
                (preprocessed['start_timestamp'].dt.date!= min(preprocessed['start_timestamp']).date()) & \
                (preprocessed['start_timestamp'].dt.date!= max(preprocessed['start_timestamp']).date())]
        daily = summarise_person.summarise_daily(preprocessed)
        daily['participant_id'] = personid
        daily = daily.fillna(0)
        alldata = alldata.append(daily)

    summary = alldata.groupby('participant_id').agg(['mean','std'])
    summary.columns = ["%s_%s"%(x[0],x[1]) for x in summary.columns]

    customcols = [x for x in summary.columns if x.startswith("custom")]
    hourlycols = [x for x in summary.columns if x.startswith("hourly")]
    othercols = [x for x in summary.columns if not (x.startswith("hourly") or x.startswith("custom"))]

    # note participant_id is the index, so doesn't have to be written explicitly
    summary[customcols].to_csv(os.path.join(outfolder,'summary_daily_custom.csv'))
    summary[hourlycols].to_csv(os.path.join(outfolder,'summary_daily_hourly.csv'))
    summary[othercols].to_csv(os.path.join(outfolder,'summary_daily.csv'))
