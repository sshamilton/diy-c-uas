#Database Abstraction Class for diy-c-uas
#SQLite DB interface
#Written by Stephen Hamilton 
#Created on 18 Sept 2017

import os.path
import sqlite3
import datetime

class NetdevDb:
    def __init__(self, dbname):
        #Check if db exists.  Create the db if it does not.
        if os.path.isfile(dbname + ".db"):
            self.conn = sqlite3.connect(dbname + ".db")
            print ("Connected to " + dbname)
        else:
            #Open and create the database and add encoding types
            self.conn = sqlite3.connect(dbname + ".db")
            c = self.conn.cursor()
            c.execute('''CREATE TABLE netdevices 
                (bssid character(12), essid varchar(255), 
                power int, channel int, enc_type int, active int, created_at int)''')
            c.execute('''CREATE TABLE locations 
                (bssid character(12), latitude float, longitude float, altitude float, created_at int)''')
            c.execute('''CREATE TABLE enctypes (id int PRIMARY KEY, name varchar(50))''')
            c.execute('''CREATE TABLE blacklist (bssid character(12), created_at int)''')
            self.conn.commit()
            c.execute("INSERT INTO enctypes VALUES('1', 'None')")
            c.execute("INSERT INTO enctypes VALUES('2', 'WPA')")
            c.execute("INSERT INTO enctypes VALUES('3', 'WPA2')")
            c.execute("INSERT INTO enctypes VALUES('4', 'WEP')")
            c.execute("INSERT INTO enctypes VALUES('5', 'OPN')")
            self.conn.commit()

            print ("Database Created")
        
    def unixtime(self, dt):
        epoch = datetime.datetime.utcfromtimestamp(0)
        return (dt - epoch).total_seconds() * 1000.0

    def mark_inactive(self):
        c = self.conn.cursor()
        c.execute("UPDATE netdevices set active = 0")


    def adddevice(self, bssid, essid, power, channel, encryption):
        currenttime = self.unixtime(datetime.datetime.now())
        if (len(bssid) == 17):
            #Strip out colons
            b = bssid.replace(":","")
        else:
            print("BSSID incorrect")
            return 1 
        if (len(essid) < 256):
            e = essid
        else:
            print("ESSID too long.")
            return 1
        p = int(power)
        
        ch = int(channel)
        if (encryption == "None"):
            enctype = 1
        elif (encryption == "WPA"):
            enctype = 2
        elif (encryption == "WPA2"):
            enctype = 3
        elif (encryption == "WEP"):
            enctype = 4
        elif (encryption == "OPN"):
            enctype = 5
        else:
            enctype = 0 #Default if none of the above
            print ("Warning undefined enc: ", encryption)
        #Check if bssid exists
        c = self.conn.cursor()
        c.execute("SELECT * from netdevices WHERE bssid = '" + b +"'")
        if (c.fetchone() is not None):
            print ("Device exists, setting active")
            c.execute("UPDATE netdevices set active = 1 where bssid= '" + b + "'")
            return 1
        else:
            print("Adding Device: ", bssid)
            c.execute("INSERT INTO netdevices(bssid, essid, power, channel, enc_type, created_at) VALUES('" + b + "', '" + e + "', " + str(p) + ", " + str(ch) + ", " + str(enctype) + ", " + str(currenttime) + ")")
            self.conn.commit() 
            return 0
  

    def addlocation(self, bssid, gpsdata):
        #Should we validate the BSSID exists in netdev? 
        #Should we only insert if location is significantly different?
        #currenttime = self.unixtime(datetime.datetime.now())  #use gps time now.
        if (len(bssid) == 17):
            #Strip out colons
            b = bssid.replace(":","")
        else:
            print("BSSID incorrect")
            return 1 
        c = self.conn.cursor()
        c.execute("INSERT INTO locations(bssid, latitude, longitude, altitude, created_at) VALUES('" + b + "', " + str(gpsdata['latitude']) + ", " + str(gpsdata['longitude']) + ", " + str(gpsdata['altitude']) + ", " + gpsdata['timestamp'] + ")")
        self.conn.commit()
        return 0
  

    def blacklist(self, bssid):
        currenttime = self.unixtime(datetime.datetime.now())
        if (len(bssid) == 17):
            #Strip out colons
            b = bssid.replace(":","")
        else:
            print("BSSID incorrect")
            return 1
        c = self.conn.cursor()
        c.execute("SELECT * from blacklist WHERE bssid = '" + b +"'")
        if (c.fetchone() is not None):
            print ("Device already blacklisted")
            return 1
        else:
            c.execute("INSERT INTO blacklist(bssid, created_at) VALUES('" + b + "', " + str(currenttime) + ")")
            self.conn.commit()
        return 0

    def get_blacklisted(self):
        blist = []
        c = self.conn.cursor()
        c.execute("select substr(blacklist.bssid, 0, 7) as bl, netdevices.bssid as bssid, channel from blacklist, netdevices where bl=substr(netdevices.bssid, 0, 7) and netdevices.active=1")
        for row in c.fetchall():
            #Deauth all blacklisted
            bssid = row[1]
            bssid = bssid[0:2] + ":" + bssid[2:4] + ":" + bssid[4:6] + ":"+ bssid[6:8] + ":"+ bssid[8:10] + ":"+ bssid[10:12]
            blist.append({'bssid': bssid, 'channel': row[2]})
            
        return blist

    def deviceswithlocations(self):
        c = self.conn.cursor()
        c.execute("SELECT netdevices.bssid, essid, power, channel, enctypes.name, "
            "netdevices.created_at, latitude, longitude, locations.created_at "
            "FROM netdevices, locations, enctypes "
            "WHERE netdevices.bssid = locations.bssid "
            "AND netdevices.enc_type = enctypes.id")
        for row in c.fetchall():
            print (row)

