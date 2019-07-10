from subprocess import PIPE, Popen
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

# jwt = OL.get_jwt(secrets, user="cafe")['access_token']
jwt = args.jwt
configuration = OL.get_config(jwt, local=args.local)

edmAPI = openlattice.EdmApi(openlattice.ApiClient(configuration))
dataAPI = openlattice.DataApi(openlattice.ApiClient(configuration))
searchAPI = openlattice.SearchApi(openlattice.ApiClient(configuration))
orgAPI = openlattice.OrganizationsApi(openlattice.ApiClient(configuration))
principalAPI = openlattice.PrincipalApi(openlattice.ApiClient(configuration))
permissionsAPI = openlattice.PermissionsApi(openlattice.ApiClient(configuration))

# get organization

# cafe_org_id = '7349c446-2acc-4d14-b2a9-a13be39cff93'
# cafe_org = orgAPI.get_organization(cafe_org_id)
if not args.local:
    org = studyconfig['studies'][study]['organisation']
    orgid = studyconfig['organisations'][org]['id']
    organisation = orgAPI.get_organization(orgid)

## create flight

tud_flight = os.path.join(integration_dir, "time_use_diary_template.yaml")
tmpfile = "/tmp/flight_%s.yaml"%study
s = open(tud_flight).read()
s = s.replace('CAFE_ES_', 'CAFE_TUD_%s_'%study)
s = s.replace("CAFE_CONDITION_STUDY", study)
f = open(tmpfile, 'w')
f.write(s)
f.close()

fl = flight.flight(edmAPI)
fl.deserialise(tmpfile)
entitysets = fl.get_all_entitysets(
    remove_prefix="CAFE_TUD_%s_"%study,
    add_prefix="%s: "%study,
    add_suffix=" (TUD - CAFE)",
    contacts = studyconfig['studies'][study]['emails'])

for entityset in entitysets:
    
    print("setting up %s ..."%entityset['name'])

    # create entity set

    try:
        edmAPI.create_entity_sets(entity_set=[entityset])
    except openlattice.rest.ApiException:
        print("This entity already exists, clearing now: %s"%entityset['name'])
        entsetid = edmAPI.get_entity_set_id(entityset['name'])
        dataAPI.delete_all_entities_from_entity_set(entsetid, "Hard")
    if not args.local:
        entsetid = edmAPI.get_entity_set_id(entityset['name'])

        # assign owner permissions

        for role in ["OWNER", "READ", "READ DEIDENTIFIED"]:
            roleperm = role.split(" ")[0]
        
            rolid = [x for x in organisation.roles if x.title.endswith(role.replace("Z", "S"))][0].principal.id
            aces = [openlattice.Ace(
                principal = openlattice.Principal(type="ROLE", id= rolid),
                permissions = [roleperm]
            )]
        
            acldata = openlattice.AclData(action = "ADD",
                acl = openlattice.Acl(acl_key = [entsetid],aces = aces))
        
            permissionsAPI.update_acl(acldata)
            properties = edmAPI.get_entity_type(entityset['entityTypeId'])
            propids = list(set(properties.properties + properties.key))
            for propid in propids:
                if propid == '5260cfbd-bfa4-40c1-ade5-cd83cc9f99b2' and role == "READ DEIDENTIFIED":
                    continue
        
                acldata = openlattice.AclData(action = "ADD",
                    acl = openlattice.Acl(acl_key = [entsetid,propid],aces = aces))
                permissionsAPI.update_acl(acldata)

statement = "{shuttle} --flight {flight} --token {token} --csv \"{csv}\" --environment {local} --upload-size 500".format(
    shuttle = shuttle,
    flight = tmpfile,
    token = jwt,
    csv = cleanfile,
    local = "LOCAL" if args.local else "PROD_INTEGRATION"
)
print(statement)
p = Popen(statement, shell=True, stdout = PIPE, stderr= PIPE)
stdout, stderr = p.communicate()
print ("stdout: '%s'" % stdout.decode("utf-8") )
print ("stderr: '%s'" % stderr.decode("utf-8") )
