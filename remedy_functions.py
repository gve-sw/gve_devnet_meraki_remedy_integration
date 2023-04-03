#!/usr/bin/env python3
"""
Copyright (c) 2023 Cisco and/or its affiliates.

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
import requests
import json, os
from pprint import pprint
from dotenv import load_dotenv

# this function will retrieve and return an access token for Remedy API calls
def get_token(remedy):
    login_endpoint = "/api/jwt/login"

    headers = {
        "Content-type": "application/x-www-form-urlencoded"
        }

    body = {
        "username": remedy["username"],
        "password": remedy["password"]
        }

    response = requests.post(remedy["url"]+login_endpoint, headers=headers,
                             data=body, verify=False)
    print(response.text)

    return response.text

# this function will create an incident ticket with pre-set values in Remedy
def create_incident(remedy, event):
    incident_endpoint = "/api/arsys/v1/entry/HPD:IncidentInterface_Create"

    # to change ticket fields such as the description, impact, urgency, status, etc. modify the following values
    payload = json.dumps({
        "values": {
            "Description": "Meraki REST API: Incident Creation",
            "Detailed_Decription": "Meraki REST API TEST",
            "Product Name": "BMC Remedy",
            "Login_ID": remedy["username"],
            "Impact": "4-Minor/Localized",
            "Urgency": "4-Low",
            "Status": "Assigned",
            "Reported Source": "Direct Input",
            "Service_Type": "User Service Restoration",
            "z1D_Action": "CREATE"
            }
        })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'AR-JWT {}'.format(remedy["token"])
        }

    response = requests.post(remedy["url"]+incident_endpoint, headers=headers, data=payload)

    print(response.status_code)
