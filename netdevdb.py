#Database Abstraction Class for diy-c-uas
#SQLite DB interface
#Written by Stephen Hamilton 
#Created on 18 Sept 2017

import os.path
import sqlite3

class NetdevDb:
    def __init__(self, dbname):
        #Check if db exists.  Create the db if it does not.
        if os.path.isfile(dbname + ".db"):
            self.conn = sqlite3.connect(dbname + ".db")
            print ("Connected to " + dbname)
        else:
            #Open and create the database and add encoding types
            self.conn = sqlite3.connect(dbname + ".db")
            c.execute('''CREATE TABLE netdevices (bssid character(12), essid varchar(255), power int, channel int, enc_type int, created_at int)''')
            c.execute('''CREATE TABLE locations (lat float, long float, created_at int)''')
            c.execute('''CREATE TABLE enctypes (id int PRIMARY KEY, name varchar(50), created_at int)''')
            c.execute("INSERT INTO enctypes (1, 'None')")
            c.execute("INSERT INTO enctypes (2, 'WPA')")
            c.execute("INSERT INTO enctypes (3, 'WPA2')")
            c.execute("INSERT INTO enctypes (4, 'WEP')")
            self.conn.commit()

            print ("Database Created")
        
    def adddevice(self, bssid, essid, power, channel, encryption):

    def addlocation(self, bssid, lat, long):
