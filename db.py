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
import sqlite3
from sqlite3 import Error
from pprint import pprint

# connect to database
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)

        return conn
    except Error as e:
        print(e)

        return None

# create empty tables to hold routers, switches, and aps
def create_tables(conn):
    c = conn.cursor()

    c.execute("""
              CREATE TABLE IF NOT EXISTS routers
              ([serial] TEXT PRIMARY KEY,
               [status] TEXT)
              """)

    c.execute("""
              CREATE TABLE IF NOT EXISTS switches
              ([serial] TEXT PRIMARY KEY,
               [connection] TEXT,
               [status] TEXT,
              FOREIGN KEY (connection) REFERENCES routers (serial))
              """)

    c.execute("""
              CREATE TABLE IF NOT EXISTS aps
              ([serial] TEXT PRIMARY KEY,
               [connection] TEXT,
               [status] TEXT,
              FOREIGN KEY (connection) REFERENCES switches (serial))
              """)

    conn.commit()

# return all routers added to the database
def query_all_routers(conn):
    c = conn.cursor()

    c.execute("""
              SELECT *
              FROM routers
              """)
    routers = c.fetchall()

    return routers

# return all switches added to the database
def query_all_switches(conn):
    c = conn.cursor()

    c.execute("""
              SELECT *
              FROM switches
              """)
    switches = c.fetchall()

    return switches

# return all aps added to the database
def query_all_aps(conn):
    c = conn.cursor()

    c.execute("""SELECT *
              FROM aps
              """)
    aps = c.fetchall()

    return aps

# return the status of a specific router
def query_router_status(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT status
              FROM routers
              WHERE serial = ?""",
              (serial,))
    router_status = c.fetchall()

    return router_status

# return the status of a specific switch
def query_switch_status(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT status
              FROM switches
              WHERE serial = ?""",
              (serial,))
    switch_status = c.fetchall()

    return switch_status

# return the status of a specific ap
def query_ap_status(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT status
              FROM aps
              WHERE serial = ?""",
              (serial,))
    ap_status = c.fetchall()

    return ap_status

# return the connection of a specific switch
def query_switch_connection(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT connection
              FROM switches
              WHERE serial = ?""",
              (serial,))

    connection = c.fetchall()

    return connection

# return the connection of a specific ap
def query_ap_connection(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT connection
              FROM aps
              WHERE serial = ?""",
              (serial,))

    connection = c.fetchall()

    return connection

# change the status of a specific device
def update_device_status(conn, device_type, serial, status):
    c = conn.cursor()

    if device_type == "router":
        table = "routers"
    elif device_type == "switch":
        table = "switches"
    elif device_type == "AP":
        table = "aps"
    else:
        print("Unable to update device status because device type is not recognized")

        return

    update_statement = "UPDATE " + table + " SET status = '" + status + "' WHERE serial = ?"
    c.execute(update_statement, (serial,))
    conn.commit()

# return serial number of one switch specified by serial number
def query_specific_switch(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT serial
              FROM switches
              WHERE serial = ?""",
              (serial,))

    switch = c.fetchall()

    return switch

# return serial number of one router specified by serial number
def query_specific_router(conn, serial):
    c = conn.cursor()

    c.execute("""SELECT serial
              FROM routers
              WHERE serial = ?""",
              (serial,))

    router = c.fetchall()

    return router

# add or update router to database
def add_router(conn, serial, status):
    c = conn.cursor()

    c.execute("""INSERT OR REPLACE INTO routers (serial, status)
              VALUES (?, ?)""",
              (serial, status))

# add or update switch to database
def add_switch(conn, serial, status, connection=None):
    c = conn.cursor()

    if connection is None:
        c.execute("""INSERT OR REPLACE INTO switches (serial, status)
                  VALUES (?, ?)""",
                  (serial, status))
    else:
        c.execute("""INSERT OR REPLACE INTO switches (serial, status, connection)
                  VALUES (?, ?, ?)""",
                  (serial, status, connection))

    conn.commit()

# add or update ap to database
def add_ap(conn, serial, status, connection=None):
    c = conn.cursor()

    if connection is None:
        c.execute("""INSERT OR REPLACE INTO aps (serial, status)
                  VALUES (?, ?)""",
                  (serial, status))
    else:
        c.execute("""INSERT OR REPLACE INTO aps (serial, status, connection)
                  VALUES (?, ?, ?)""",
                  (serial, status, connection))

    conn.commit()

# close connection to database
def close_connection(conn):
    conn.close()


# if running this python file, create connection to database, create tables, and print out the results of queries of every table
if __name__ == "__main__":
    conn = create_connection("sqlite.db")
    create_tables(conn)
    pprint(query_all_routers(conn))
    pprint(query_all_switches(conn))
    pprint(query_all_aps(conn))
    close_connection(conn)
