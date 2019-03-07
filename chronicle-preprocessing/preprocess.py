from chroniclepy import preprocessing
from collections import Counter
import pandas as pd
import openlattice
import datetime
import requests
import yaml
import sys
import os

basedir = "/chroniclepy"
# basedir="/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/chronicle-preprocessing/"
datadir = os.path.join(basedir, "data")

sys.path.append(basedir)
from utils import OL

## grab username and password from secrets file

with open(os.path.join(basedir,"secrets.yaml"), 'r') as fl:
    secrets = yaml.load(fl)

# get configuration

jwt = OL.get_jwt(secrets)['access_token']
configuration = OL.get_config(jwt)
headers = {"Authorization": "Bearer %s"%jwt}
edmAPI = openlattice.EdmApi(openlattice.ApiClient(configuration))
dataAPI = openlattice.DataApi(openlattice.ApiClient(configuration))
searchAPI = openlattice.SearchApi(openlattice.ApiClient(configuration))

# get all chronicle_participant datasets

entsets  = edmAPI.get_all_entity_sets()
studies = [x for x in entsets if x != None and 'chronicle_participants' in x.name]

# define chronicle app dataset and requested columns

chronicle_app_id = edmAPI.get_entity_set_id('chronicle_app_data')
cols = [
    {"namespace": 'general', "name": 'fullname'},
    {"namespace": 'ol', "name": 'recordtype'},
    {"namespace": 'ol', "name": 'timezone'},
    {"namespace": "ol", "name": "datelogged"}
    ]
colids = [edmAPI.get_property_type_id(x['namespace'], x['name']) for x in cols]

counts = []
for study in studies:
# study = studies[1]
    # print("Processing study %s."%study.name)
    # load study participants
    chronicle_study_UUID = study.name.split("_")[-1]
    chronicle_entityset_id = edmAPI.get_entity_set_id(study.name)
    chronicle_study_id = study.name.split("_")[-1]
    chronicle_study_people_data =  pd.DataFrame(dataAPI.load_entity_set_data(chronicle_entityset_id))

    newtable = pd.DataFrame()

    for idx, row in chronicle_study_people_data.iterrows():
        if str(row['nc.SubjectIdentification']) == 'nan':
            print("Study: %s - participant: %s - MISSING USER ID."%(study.name, row['openlattice.@id'][0]))
            continue
        print("Study: %s - participant: %s - nc.subjectIdentification: %s"%(study.name, str(row['openlattice.@id'][0]), str(row['nc.SubjectIdentification'][0])))
        # row = chronicle_study_people_data.iloc[0]
        # for each participant: load edges and create filter

        person_id = row['nc.SubjectIdentification'][0]
        outfilename = os.path.join(datadir,"ChronicleData_preprocessed_%s.csv"%person_id)
        if os.path.exists(outfilename):
            continue

        ent_id = row['openlattice.@id'][0]
        edges = searchAPI.execute_entity_neighbor_search(chronicle_entityset_id, ent_id)
        devices = [x.neighbor_id for x in edges if x.neighbor_entity_set.name == 'chronicle_device']
        if len(Counter(devices).keys()) > 1:
            print("DO SOMETHING !")

        # for device in devices:
        #     device_edges = searchAPI.execute_entity_neighbor_search(chronicle_entityset_id, ent_id)
        appdata_keys = [x.neighbor_id for x in edges if x.neighbor_entity_set.name == 'chronicle_app_data']
        if len(appdata_keys) == 0:
            print("   ---- no data.")
            continue

        print("    ---- loading data.")
        filter = openlattice.EntitySetSelection(
            ids = appdata_keys,
            properties = colids
        )

        # grab data

        userdata = dataAPI.load_filtered_entity_set_data(entity_set_id = chronicle_app_id, entity_set_selection = filter)
        userdata_reduced = [{k:v[0] for k,v in x.items()} for x in userdata if 'ol.recordtype' in x.keys() and x['ol.recordtype'][0] != "Usage Stat"]
        userdata_df = pd.DataFrame(userdata_reduced)

        # write to csv

        filename = os.path.join(datadir,"ChronicleData_%s.csv"%person_id)
        userdata_df.to_csv(filename)

        userdata_df = userdata_df.sort_values(by='ol.datelogged')
        hlp = preprocessing.read_and_clean_data(filename)
        startdt = hlp.loc[0,'dt_logged']
        enddt = hlp.loc[len(hlp)-1, 'dt_logged']
        userdata_df = hlp[(hlp['dt_logged']-startdt)  < datetime.timedelta(days=30)]
        userdata_df.to_csv(filename)
        # preprocess from csv (this extra write doesn't require changes to chroniclepy)
        print("    ---- start and end time for subject %s: %s - %s"%(str(row['nc.SubjectIdentification'][0]), str(startdt), str(enddt)))
        newtable = newtable.append({
            "ID": str(row['nc.SubjectIdentification'][0]),
            "startDT": str(startdt),
            "endDT": str(enddt)
        }, ignore_index=True)

        print("    ---- preprocessing data.")
        tmp = preprocessing.extract_usage(filename, precision = 15*60)
        if not isinstance(tmp,pd.DataFrame):
            print("WARNING: File %s does not seem to contain relevant data.  Skipping..."%filename)
            continue
        else:
            print("    ---- checking overlapping data.")
            processed = preprocessing.check_overlap_add_sessions(tmp,session_def=[5*60])
            processed['participant_id'] = person_id
            processed['study_id'] = chronicle_study_id
            os.remove(filename)
            processed['index'] = processed.index
            processed.to_csv(outfilename, index=False)
    newtable.to_csv(os.path.join(datadir,"ChronicleData_%s_dates.csv"%study.name))
