#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""

DNAC Discovery Script.

Copyright (c) 2024 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at

               https://developer.cisco.com/docs/licenses

All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.

"""

__author__ = "Rajesh Chaudhary"
__email__ = "rachaud2@cisco.com"
__version__ = "1.0"
__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.0"

import urllib3
import requests
import json
import time
import io
import sys
import csv
import pandas as pd
import argparse
from argparse import RawTextHelpFormatter
from requests.auth import HTTPBasicAuth
#from urllib3.exceptions import InsecureRequestWarning
from cat_config import CatC_IP, CatC_PORT, USERNAME, PASSWORD
import logging
requests.packages.urllib3.disable_warnings()

# -------------------------------------------------------------------
# Custom exception definitions
# -------------------------------------------------------------------
class TaskTimeoutError(Exception):
    pass

class TaskError(Exception):
    pass


def get_token(CatC_IP, CatC_PORT, USERNAME, PASSWORD):
    url = 'https://%s:%s/dna/system/api/v1/auth/token'%(CatC_IP, CatC_PORT)
    auth = HTTPBasicAuth(USERNAME, PASSWORD)
    headers = {'content-type' : 'application/json'}
    try:
        response = requests.post(url, auth=auth, headers=headers, verify=False)
        token = response.json()['Token']
        logging.info('Got Token from Catalyst Center')
        logging.debug(f'Token: {token}')
        return token
    except requests.exceptions.RequestException as err:
        logging.error(err)
        raise SystemExit()

        
#def get_device_ids(token):
#   headers = { 'x-auth-token': token,
#                'content-type': 'application/json' }
#    url = f"https://{CatC_IP}:{CatC_PORT}/dna/intent/api/v1/image/importation?version={version_name}" 
#    try:
#        response = requests.get(url, headers=headers, verify=False)
#        info = response.json()['response']
#        return info
#        #return info[0]['imageUuid']
#    except requests.exceptions.RequestException as err:
#        logging.error(err)
#        raise SystemExit()

# Get device IDs from Catalyst Center for all devices that are of platform family WLC
def get_wlc_ids(token,family_type):
    headers = { 'x-auth-token': token,
                'content-type': 'application/json' }
    url =f"https://{CatC_IP}:{CatC_PORT}/dna/intent/api/v1/network-device?family={family_type}"
    try:
        response = requests.get(url, headers=headers, verify=False)
        info = response.json()['response']
        #print(info)
        return info
        #return info[0]['id']
    except requests.exceptions.RequestException as err:
        logging.error(err)
        raise SystemExit()

# Get list of SSIDs from Catalyst Center for a given WLC
def get_SSIDs_from_WLC(token, wlc_id):
    headers = { 'x-auth-token': token,
                'content-type': 'application/json' }
    url =f"https://{CatC_IP}:{CatC_PORT}/dna/intent/api/v1/wirelessControllers/{wlc_id}/ssidDetails"
    try:
        response = requests.get(url, headers=headers, verify=False)
        info = response.json()['response']
        #print(info)
        return response.json()
    except requests.exceptions.RequestException as err:
        logging.error(err)
        raise SystemExit()
    
# Validate that the image being loaded is expected on the device family
#def validate():
     



def main():
    logging.basicConfig(
    #filename='application_run.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('starting the program.')
    

    #ver = "17.10.01.0.1444"
    #hostname = "DNA02-Edge1.csspod2.com"

    output = []
    family_type = "Wireless Controller"

    cat_token = get_token(CatC_IP, CatC_PORT, USERNAME, PASSWORD)
    wlc_info = get_wlc_ids(cat_token,family_type)
    print(type(wlc_info))
    print(wlc_info)
    #dev_info = get_device_info(cat_token,hostname)
    with open('ssid_info.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerow(['wlanId', 'wlanProfileName', 'l2Security', 'l3Security', 'ssidName', 'radioPolicy', 'adminStatus', 'managed', 'WLC Hostname'])
        for i in range(len(wlc_info)):
            wlc_id = wlc_info[i]['id']
            print(wlc_id)
            ssid_info = get_SSIDs_from_WLC(cat_token, wlc_id)

            df = pd.json_normalize(ssid_info['response'])
            #df = pd.read_json(ssid_info['response'])
            df['WLC Hostname'] = wlc_info[i]['hostname']
            df.to_csv(file, mode= 'a', header=False, index=False)

            print(ssid_info)


if __name__ == '__main__':
    main()