#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This script recreates the organisations and roles setup for a local development.
"""
        
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

# get API's
code_dir = '/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/'
with open(os.path.join(code_dir,"integration/secrets.yaml"), 'r') as fl:
    secrets = yaml.load(fl)


cafeorg = "7349c446-2acc-4d14-b2a9-a13be39cff93"
byuorg = "19393e4d-53bd-48ab-9272-9b7bb17bf6cb"
umorg = "0977afca-3298-480b-a301-b687a73de933"
wiscorg = '74889b0b-ba47-4e6b-8bea-36a7e46c33d7'
guorg = '42e53100-3e22-4e7b-90a7-e880e2e696f6'

cafejwt = "*"
jwt = "*"
for orgid in [ cafeorg, byuorg, umorg, wiscorg, guorg]:
    cafeconfiguration = OL.get_config(cafejwt, local=False)
    cafeorgAPI = openlattice.OrganizationsApi(openlattice.ApiClient(cafeconfiguration))
    org = cafeorgAPI.get_organization(orgid)
    configuration = OL.get_config(jwt, local=True)
    orgAPI = openlattice.OrganizationsApi(openlattice.ApiClient(configuration))
    orgAPI.create_organization_if_not_exists(org)


