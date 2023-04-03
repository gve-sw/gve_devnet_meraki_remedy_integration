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
import meraki
import os
from dotenv import load_dotenv
from pprint import pprint
import db

# load environmental variables
load_dotenv()

API_KEY = os.getenv("MERAKI_TOKEN")
ORG_NAME = os.getenv("MERAKI_ORG")
NET_NAME = os.getenv("MERAKI_NETWORK")

# connect to Meraki dashboard
dashboard = meraki.DashboardAPI(API_KEY, suppress_logging=True)
# connect to database
conn = db.create_connection("sqlite.db")
c = conn.cursor()

# get org id for org name in environment variables
orgs = dashboard.organizations.getOrganizations()
for org in orgs:
    if org["name"] == ORG_NAME:
        org_id = org["id"]

# get net id for net name in environment variables
networks = dashboard.organizations.getOrganizationNetworks(org_id,
                                                           total_pages="all")
for net in networks:
    if net["name"] == NET_NAME:
        net_id = net["id"]

# grab the network topology from Meraki dashboard to determine which devices are connected to each other
topology = dashboard.networks.getNetworkTopologyLinkLayer(net_id)
links = topology["links"]

connections = []
for link in links:
    serials = []
    connection = link["ends"]
    for node in connection:
        if node["node"]["type"] == "device":
            device = node["device"]
            serial = device["serial"]
            serials.append({"serial": serial})
    connections.append(serials)

for connection in connections:
    for node in connection:
        device = dashboard.devices.getDevice(node["serial"])
        if "MR" in device["model"]:
            node["type"] = "AP"
        elif "MS" in device["model"]:
            node["type"] = "switch"
        elif "MX" in device["model"]:
            node["type"] = "router"
        # get status to determine what to initialize database
        device_status = dashboard.organizations.getOrganizationDevicesStatuses(org_id,
                                                                               serials=[node["serial"]])
        if device_status[0]["status"] == "online" or device_status[0]["status"] == "alerting":
            node["status"] = "up"
        else:
            node["status"] = "down"
    if len(connection) > 1:
        device_types = {connection[0]["type"], connection[1]["type"]}
        if "AP" in device_types and "switch" in device_types:
            # check if the first connection is a switch
            if connection[0]["type"] == "switch":
                # check if switch already exists in the database
                data = db.query_specific_switch(conn, connection[0]["serial"])
                if len(data) == 0:
                    # if switch not already in the database, add it
                    db.add_switch(conn, connection[0]["serial"],
                                  connection[0]["status"])

                # now add the AP into the database
                db.add_ap(conn, connection[1]["serial"],
                          connection[1]["status"], connection[0]["serial"])
            # the first connection is not a switch, so it must be an AP
            else:
                # check if switch already exists in the database
                data = db.query_specific_switch(conn, connection[1]["serial"])
                if len(data) == 0:
                    # add switch to database
                    db.add_switch(conn, connection[1]["serial"],
                                  connection[1]["status"])

                # now add the AP to the database
                db.add_ap(conn, connection[0]["serial"],
                          connection[0]["status"], connection[1]["serial"])
        elif "switch" and "router" in device_types:
            # check if first connection is a router
            if connection[0]["type"] == "router":
                # check if router already exists in the database
                data = db.query_specific_router(conn, connection[0]["serial"])
                if len(data) == 0:
                    # router is not in database, so it must be added
                    db.add_router(conn, connection[0]["serial"],
                                  connection[0]["status"])

                # now add switch into the database
                db.add_switch(conn, connection[1]["serial"],
                              connection[1]["status"], connection[0]["serial"])
            # the first connection is not a router, so it must be a switch
            else:
                # check if router already exists in database
                data = db.query_specific_router(conn, connection[1]["serial"])
                if len(data) == 0:
                    # router is not in database and needs to be added
                    db.add_router(conn, connection[1]["serial"],
                                  connection[1]["status"])

                # now add switch into database
                db.add_switch(conn, connection[0]["serial"],
                              connection[0]["status"], connection[1]["serial"])


# print the results of all the queries to all the tables
pprint(db.query_all_routers(conn))
pprint(db.query_all_switches(conn))
pprint(db.query_all_aps(conn))

# close the database connection
db.close_connection(conn)
