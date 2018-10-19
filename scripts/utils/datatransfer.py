import os
import pandas as pd
from collections import Counter
import numpy as np
import datetime as dt

def get_attention_and_tv(subject, attentionfile,subjectinfo,attentionfolder,conditionsfolder, suffix=""):
    if attentionfile.endswith("csv"):
        data = pd.read_csv(os.path.join(attentionfolder,attentionfile))
    else:
        data = pd.read_excel(os.path.join(attentionfolder,attentionfile))

    if not pd.isnull(subjectinfo['Date']):
        date = dt.datetime.strptime(str(int(subjectinfo['Date'])),"%y%m%d")
    else:
        print("The subject information for %s has no date.  Setting date to 180721 (subject 020)."%subject)
        date = dt.datetime.strptime("180721","%y%m%d")
    videodatetime = dt.datetime.combine(date,subjectinfo['Video_Start_Time'])

    # create subjecttable with origin from the subject_info_sheet
    tvfile = os.path.join(conditionsfolder,"TV%s.csv"%suffix)
    attentionfile = os.path.join(conditionsfolder,"attention%s.csv"%suffix)
    subjecttable = pd.DataFrame({
            "file": ["conditions/"+os.path.basename(tvfile),"conditions/"+os.path.basename(attentionfile)],
            "origin": [videodatetime]*2
            })

    # separate tv and attention data
    data.columns = data.columns.str.lower()
    TV = data[['tv.ordinal','tv.onset',
                     'tv.offset','tv.code01']].dropna()
    TV.columns = ['ordinal', 'onset', 'offset', 'code']
    attention = data[['attention.ordinal','attention.onset', 'attention.offset','attention.code01']]
    attention.columns = ['ordinal','onset','offset','code']

    # add TV conditions to file
    if subject == "WI_AMP_006":
        TV['code'] = [x.split("_")[0] for x in TV.code]
        TV['video'] = ["", subjectinfo['Cond1'],subjectinfo['Cond1'],subjectinfo['Cond2'],subjectinfo['Cond3']]
    elif subjectinfo.name == 'WI_AMP_020_A':
        TV['video'] = ["", subjectinfo['Cond1']]
    elif subjectinfo.name == 'WI_AMP_020_B':
        TV['video'] = ["Psych", "TL", "NoTV"]
    else:
        if TV.code[0].replace(" ","")=='Baseline':
            TV['video'] = ["",subjectinfo['Cond1'],subjectinfo['Cond2'],subjectinfo['Cond3']]

    return subjecttable, TV, attention
