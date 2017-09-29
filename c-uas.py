#!/usr/bin/python3
import logging
import argparse
from netdevdb import NetdevDb #Abstraction layer for db connectivity
from pyrcrack.scanning import Airodump
import serial # For GPS

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

def scan(netdb):
    """
    Scan: Runs airodump-ng to characterize the environment.
    Returns: [string] containing the detected MAC addresses
    """
    # Setup the wireless interface to listen on
    interface = 'wlp3s0' #Change this for the pi to something like wlan0
    logging.debug("started scan")
    wifi = Airodump(interface)
    wifi.start()
    scanres = wifi.tree

    #Now add access points to db
    for bssid in wifi.tree:
        netdb.adddevice(bssid, wifi.tree[bssid]['ESSID'], wifi.tree[bssid]['Power'], 
            wifi.tree[bssid]['channel'], wifi.tree[bssid]['Privacy'])
        netdb.addlocation(bssid, 34.1, -74.1) #Get GPS coordinates.  This is a placeholder.        
    
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


def deauth_targets(attack_pairs):
    """
    Detauth Targets: Performs a replay attack against the listed targets
    Input: [(string,int)] with the (MAC,channel) to target
    """
    logging.debug("deauth targets")
    logging.debug(attack_pairs)
    pass

    def getlocation(self, gpsdevice): #Pass in gps interface
        #Get current location and return it as a key pair
        ser = serial.Serial()
        ser.port = gpsdevice
        ser.open()
        
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

    #while True:
    for i in range(2):
        networks = scan(netdb)
        print ("scan complete")
        netdb.deviceswithlocations() #Show what was scanned
        targets = select_targets(networks)
        if len(targets) > 0:
            attack_pairs = refine_targets(targets)
            deauth_targets(attack_pairs)


if __name__ == "__main__":
    main()
