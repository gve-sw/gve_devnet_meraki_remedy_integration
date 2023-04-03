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
from flask import Flask, request, json
import os
from dotenv import load_dotenv
from pprint import pprint
import remedy_functions
import db

# Global variables
load_dotenv()

# The remedy data structure will hold all the info to make API requests to Remedy
remedy = {
    "url": os.environ["REMEDY_URL"],
    "username": os.environ["REMEDY_USERNAME"],
    "password": os.environ["REMEDY_PASSWORD"]
}


app = Flask(__name__)

"""
The webhooks will send information to this web server, and this function
provides the logic to parse the Meraki alert and create a Remedy ticket
"""
@app.route("/", methods=["GET", "POST"])
def alert():
    # If the method is POST, then an alert has sent a webhook to the web server
    if request.method == "POST":
        data = request.json # Retrieve the json data from the request - contains alert info
        pprint(data)

        # The database holds information about the status of the Meraki devices and the topology of the network
        conn = db.create_connection("sqlite.db")

        # Retrieve an API token from Remedy and save it to the data structure
        token = remedy_functions.get_token(remedy)
        remedy["token"] = token

        # Now we will parse what the alert type is - we will generate tickets for alert types indicating switches, routers, and aps are down

        if data["alertType"] == "switches went down":
            serial = data["deviceSerial"]
            # check what the switch status is
            switch_status = db.query_switch_status(conn, serial)
            if switch_status[0][0] == "up":
                # The switch is now down, so we need to update the database to reflect this
                db.update_device_status(conn, "switch", serial, "down")

                # Now we need to check to see if the switch connection is also down before we create a ticket
                connection = db.query_switch_connection(conn, serial)
                if connection[0][0] is not None:
                    router_status = db.query_router_status(conn, connection[0][0])
                    # If the router status is up, we create a ticket
                    if router_status[0][0] == "up":
                        event = {
                            "description": "Meraki REST API: Incident Creation\n switch " + serial + " in network " + data["networkName"] + " is down."
                        }

                        remedy_functions.create_incident(remedy, event)
                        print("Ticket created for the switch")
                    else:
                        print("No ticket needed for the switch")
                # there is no connection to the switch, we should create a ticket
                else:
                    event = {
                        "description": "Meraki REST API: Incident Creation\n switch " + serial + " in network " + data["networkName"] + " is down."
                    }

                    remedy_functions.create_incident(remedy, event)
                    print("Ticket created for the switch")
            else:
                # switch is already down, ticket should have already been created
                print("No ticket created, switch is already down. Check for existing ticket")
        elif data["alertType"] == "Cellular went down":
            serial = data["deviceSerial"]
            # check what the router status is
            router_status = db.query_router_status(conn, serial)
            if router_status[0][0] == "up":
                # The router is now down, so we need to update the database to reflect this
                db.update_device_status(conn, "router", serial, "down")

                # Now we create the ticket
                event = {
                    "description": "Meraki REST API: Incident Creation\n Router " + serial + " in network " + data["networkName"] + " is down."
                }

                remedy_functions.create_incident(remedy, event)
                print("Ticket created for the router")
            else:
                # router is already down, ticket should have already been created
                print("No ticket created, router is already down. Check for existing ticket")
        elif data["alertType"] == "APs went down":
            serial = data["deviceSerial"]
            # check what the ap status is
            ap_status = db.query_ap_status(conn, serial)
            if ap_status[0][0] == "up":
                # The AP is down, so we need to update the database to reflect this
                db.update_device_status(conn, "AP", serial, "down")

                # Now we need to check to see if the AP connection is also down before we create a ticket
                connection = db.query_ap_connection(conn, serial)
                switch_status = db.query_switch_status(conn, connection[0][0])
                # If the switch status is up, we create a ticket
                if switch_status[0][0] is not None:
                    if switch_status[0][0] == "up":
                        event = {
                            "description": "Meraki REST API: Incident Creation\n AP " + serial + " in network " + data["networkName"] + " is down."
                        }

                        remedy_functions.create_incident(remedy, event)
                        print("Ticket created for the AP")
                    else:
                        print("No ticket created for the AP")
                else:
                    # ap is not connected to device in database, create a ticket
                    event = {
                        "description": "Meraki REST API: Incident Creation\n AP " + serial + " in network " + data["networkName"] + " is down."
                    }

                    remedy_functions.create_incident(remedy, event)
                    print("Ticket created for the AP")
            else:
                # AP is already down, ticket should have already been created
                print("No ticket created, AP is already down. Check for existing ticket")
        elif data["alertType"] == "switches came up":
            serial = data["deviceSerial"]
            # The switch is up, so we need to update the database to reflect this
            db.update_device_status(conn, "switch", serial, "up")
        elif data["alertType"] == "Cellular came up":
            serial = data["deviceSerial"]
            # The router is up, so we need to update the database to reflect this
            db.update_device_status(conn, "router", serial, "up")
        elif data["alertType"] == "APs came up":
            serial = data["deviceSerial"]
            # The AP is up, so we need to update the database to reflect this
            db.update_device_status(conn, "AP", serial, "up")

        db.close_connection(conn)

    return 'Webhook receiver is running - check the terminal for alert information'


if __name__ == '__main__':
    app.run(debug=True)
