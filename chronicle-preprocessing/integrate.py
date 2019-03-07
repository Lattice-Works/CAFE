import pandas as pd
import yaml
import sys
import os

sys.path.append("/chroniclepy")
from utils import flight

basedir = "/chroniclepy"
datadir = "/chroniclepy/data"


with open(os.path.join(basedir,"secrets.yaml"), 'r') as fl:
    secrets = yaml.load(fl)

datafiles = [x for x in os.listdir(datadir) if "ChronicleData_preprocessed" in x and not 'ChronicleData_chronicle_participants' in x]

for datafile in datafiles:

    data = pd.read_csv(os.path.join(datadir, datafile))

    studyId = data.study_id.iloc[0]
    participantId = data.participant_id.iloc[0]
    print("==================================================================")
    print("Integrating study %s - participant %s."%(studyId, participantId))
    print("==================================================================")
    flight_map = flight.get_flight(studyId)

    with open(os.path.join(basedir, "flight.yaml"), "w") as fl:
        fl.write(flight_map)

    cmd = "shuttle --flight {flight} --user {username} --password {password} --csv {csv} --environment PRODUCTION".format(
        flight = os.path.join(basedir, "flight.yaml"),
        username = secrets['username'],
        password = secrets['password'],
        csv = os.path.join(datadir, datafile)
    )

    process = os.popen(cmd)
    preprocessed = process.read()
    print(preprocessed)
    process.close()
