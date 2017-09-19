#Test script to make sure netdevdb is working correctly.
from netdevdb import NetdevDb

#Create a sample database

db = NetdevDb("sample")

#Add a network device

db.adddevice("00:00:00:AA:AA:AA", "Free Wifi", 62, 1, "WEP")

db.addlocation("00:00:00:AA:AA:AA", 34.1, -74.1)

db.deviceswithlocations()

