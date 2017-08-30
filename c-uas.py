#!/usr/bin/python3
import logging
import argparse


def init():
    """
    Initialization: checks for the presence of necessary tools and configures
    the logging environment.
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

def scan():
    """
    Scan: Runs airodump-ng to characterize the environment.
    Returns: [string] containing the detected MAC addresses
    """
    pass


def select_targets():
    """
    Target Selection: Compares a list of observed MAC addresses against MAC
    addresses identified as belonging to sUAS systems.
    Input: [string] containing MAC addresses from scan
    Returns: [string] containing target MAC addresses
    """
    pass


def refine_targets():
    """
    Target Refinement: Performs additional scans to gain the required
    information necessary to perform the attack such as the active channel.
    Input: [string] containing observed target MAC addresses
    Returns: [(string,int)] with the (MAC,channel) of each target
    """
    pass


def deauth_targets():
    """
    Detauth Targets: Performs a replay attack against the listed targets
    Input: [(string,int)] with the (MAC,channel) to target
    """
    pass


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


if __name__ == "__main__":
    main()
