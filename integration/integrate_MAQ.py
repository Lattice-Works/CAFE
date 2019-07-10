from flighttools import flight
import pandas as pd
import openlattice
import argparse
import requests
import string
import yaml
import uuid
import sys
import os

sys.path.append("/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/integration")
from utils import OL

# DEFINE CONSTANTS

parser = argparse.ArgumentParser()
parser.add_argument('--study', dest="study")
parser.add_argument('--cleanfile', dest='cleanfile')
parser.add_argument('--codedir', dest='codedir')
parser.add_argument('--shuttle', dest='shuttle')
parser.add_argument('--integrationsdir', dest='integrationsdir')
parser.add_argument('--jwt', dest='jwt')
parser.add_argument('--local', dest='local', action='store_true')
args = parser.parse_args()

integration_dir = args.integrationsdir
shuttle = args.shuttle
code_dir = args.codedir
cleanfile = args.cleanfile
study = args.study

# get flight template and studies

with open(os.path.join(code_dir,"integration/config.yaml"), 'r') as fl:
    studyconfig = yaml.load(fl)

# get API's
with open(os.path.join(code_dir,"integration/secrets.yaml"), 'r') as fl:
    secrets = yaml.load(fl)

jwt = OL.get_jwt(secrets, user="cafe", local=True)['access_token']
jwt = args.jwt

configuration = OL.get_config(jwt, local=args.local)
with open(os.path.join(code_dir, "integration/config.yaml"), 'r') as fl:
    config = yaml.load(fl)

edmAPI = openlattice.EdmApi(openlattice.ApiClient(configuration))
dataAPI = openlattice.DataApi(openlattice.ApiClient(configuration))
searchAPI = openlattice.SearchApi(openlattice.ApiClient(configuration))
orgAPI = openlattice.OrganizationsApi(openlattice.ApiClient(configuration))
permissionsAPI = openlattice.PermissionsApi(openlattice.ApiClient(configuration))

# get organization

if not args.local:
    org = studyconfig['studies'][study]['organisation']
    orgid = studyconfig['organisations'][org]['id']
    organisation = orgAPI.get_organization(orgid)

## create flight
flightfiles = config['studies'][study]['MAQflights']

for flightfile in flightfiles:
    
    # flightfile =  flightfiles[2]
    print("Integrating %s"%flightfile)

    tud_flight = os.path.join(integration_dir, flightfile)
    flightpart = flightfile.split("_")[2].split(".")[0]
    tmpfile = "/tmp/flight_%s_%s.yaml"%(flightpart, study)
    s = open(tud_flight).read()
    s = s.replace('CAFE_MAQ_', 'CAFE_MAQ_%s_'%study)
    f = open(tmpfile, 'w')
    f.write(s)
    f.close()


    fl = flight.flight(edmAPI)
    fl.deserialise(tmpfile)
    entitysets = fl.get_all_entitysets(
        remove_prefix="CAFE_MAQ_%s_"%study,
        add_prefix="%s: "%study,
        add_suffix=" (MAQ - CAFE)",
        contacts = studyconfig['studies'][study]['emails'])

    for entityset in entitysets:

        # create entity set

        try:
            edmAPI.create_entity_sets(entity_set=[entityset])
        except openlattice.rest.ApiException:
            print("This entity already exists, not deleting anything for: %s"%entityset['name'])
            entsetid = edmAPI.get_entity_set_id(entityset['name'])
            dataAPI.delete_all_entities_from_entity_set(entsetid, "Hard")
            # edmAPI.delete_entity_set(entsetid)
            # edmAPI.create_entity_sets(entity_set=[entityset])
        entsetid = edmAPI.get_entity_set_id(entityset['name'])

        # add to organisation
        
        if not args.local:
            meta_data_update = openlattice.MetaDataUpdate(
                organization_id = orgid
            )
            edmAPI.update_entity_set_meta_data(
                entity_set_id = entsetid,
                meta_data_update = meta_data_update
            )
            
            # assign owner permissions
            
            for role in ['OWNER', "READ", "MATERIALIZE"]:
            
                rolid = [x for x in organisation.roles if role.replace("Z", "S") in x.title][0].principal.id
                aces = [openlattice.Ace(
                    principal = openlattice.Principal(type="ROLE", id= rolid),
                    permissions = [role]
                )]
            
                acldata = openlattice.AclData(action = "ADD",
                    acl = openlattice.Acl(acl_key = [entsetid],aces = aces))
            
                permissionsAPI.update_acl(acldata)
                properties = edmAPI.get_entity_type(entityset['entityTypeId'])
                propids = list(set(properties.properties + properties.key))
                for propid in propids:
                    acldata = openlattice.AclData(action = "ADD",
                        acl = openlattice.Acl(acl_key = [entsetid,propid],aces = aces))
                    permissionsAPI.update_acl(acldata)

    statement = "{shuttle} --flight {flight} --token {token} --csv \"{csv}\" --environment  {local} ".format(
        shuttle = shuttle,
        flight = tmpfile,
        token = jwt,
        csv = cleanfile,
        local = "LOCAL" if args.local else "PROD_INTEGRATION"
    )

    print(statement)

    done = os.popen(statement)
    print(done.read())
