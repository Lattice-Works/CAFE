import pandas as pd
import openlattice
import yaml
import sys
import os

# LOCALHOST SETTINGS
# basedir = "/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/chronicle-integration/"
# datadir = os.path.join(basedir, "data")
# shuttle = "/Users/jokedurnez/Documents/openlattice/shuttle/shuttle-0.0.4-SNAPSHOT/bin/shuttle"
# environment = "LOCAL"

# DOCKER SETTINGS
basedir = "/chroniclepy"
datadir = "/chroniclepy/data"
shuttle = "shuttle"
environment = "PRODUCTION"
jwt = "**"

sys.path.append(basedir)
from utils import flight

datafiles = [x for x in os.listdir(datadir) if "ChronicleData_FIRE" in x]

#### TEMP ###
# baseurl = 'http://localhost:8080'
# 
# configuration = openlattice.Configuration()
# configuration.host = baseurl
# configuration.api_key_prefix['Authorization'] = 'Bearer'
# configuration.api_key['Authorization'] = jwt
# 
# edmAPI = openlattice.EdmApi(openlattice.ApiClient(configuration))
#########

for datafile in datafiles:
    
    print("==================================================================")
    print("Integrating file %s"%datafile)
    print("==================================================================")

    parsed = datafile.split("__")
    
    chronicle_app_data_entset = "chronicle_app_data"
    chronicle_recorded_by_entset = "chronicle_recorded_by"
    chronicle_devices_entset = "chronicle_device"
    chronicle_participants_entset = "chronicle_participants_%s"%parsed[2]
    subject_id = parsed[3]
    device_id = parsed[4].split(".")[0]
    
    ######## TEMP: LOCALHOST #######
    # entsetdict = {
    #  chronicle_app_data_entset: '14923c22-ac79-4efb-b298-c54c698b84de',
    #  chronicle_devices_entset: '58b3a5cd-8806-400e-b91d-5ae314063378',
    #  chronicle_recorded_by_entset: '9b44a35d-d414-4f7e-929a-92175017b809',
    #  chronicle_participants_entset: '31cf5595-3fe9-4d3e-a9cf-39355a4b8cab'
    # }
    # 
    # for entset in [chronicle_app_data_entset, chronicle_devices_entset, chronicle_recorded_by_entset, chronicle_participants_entset]:
    #     try:
    #         eid = edmAPI.get_entity_set_id(entset)
    #     except openlattice.rest.ApiException as exc:
    #         edmAPI.create_entity_sets([
    #             openlattice.EntitySet(
    #                 name = entset,
    #                 title = entset,
    #                 entity_type_id = entsetdict[entset],
    #                 contacts = ['joke@openlattice.com']
    #             )
    #         ])
    
    flight_map = flight.get_flight(chronicle_app_data_entset, chronicle_devices_entset, chronicle_participants_entset, subject_id, device_id, chronicle_recorded_by_entset)

    with open(os.path.join(basedir, "flight.yaml"), "w") as fl:
        fl.write(flight_map)

    cmd = "{shuttle} --flight {flight} --token {jwt} --csv {csv} --environment {environment}".format(
        shuttle = shuttle,
        flight = os.path.join(basedir, "flight.yaml"),
        jwt = jwt,
        csv = os.path.join(datadir, datafile),
        environment = environment
    )

    process = os.popen(cmd)
    preprocessed = process.read()
    print(preprocessed)
    process.close()
