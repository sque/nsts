#!/usr/bin/env python
'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, argparse, sys
from nsts.client import NSTSClient
from nsts.server import NSTSServer
from nsts.tests import *
from nsts import output

parser = argparse.ArgumentParser(
        epilog="This application was developed for the need of "
        "benchmarking wireless links at herakleion wireless metropolitan network (hwmn.org).")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-c", "--connect", help="connect to server.", type=str)
group.add_argument("-s","--server", help="start in server mode.", action="store_true")
list_tests = group.add_argument("--list-tests", help="list all available tests.", action="store_true")
parser.add_argument("-d", "--debug", 
                    help="select level of logging. 0 will log everything (default {0})".format(logging.WARNING), 
                    type=int, default = logging.WARNING)
parser.add_argument("--samples", 
                    help="how many times to execute a test (default 1)",
                    default=1, type=int)
parser.add_argument("--sample-interval",
                    help="The interval time between samples in seconds. (default 0.0sec)",
                    default = 0.0, type=float)
parser.add_argument("--tests", help="a comma separated list of all tests to execute", default="iperf_tcp_send")
args = parser.parse_args()

# Prepare logging
logging.basicConfig(level = args.debug)

if args.list_tests:
    # List tests mode
    print "Tests currently installed "
    print "-------------------------"
    for test in base.get_enabled_tests().values():
        print " * [{0}] {1}".format(test.name, test.friendly_name)
elif args.server:
    # Server Mode
    server = NSTSServer()
    server.serve()
else:
    # Client Mode
    client = NSTSClient(args.connect)
    client.connect()
    
    # Validate tests
    tests = args.tests.split(",")
    for test in tests:
        if not base.is_test_enabled(test):
            print "Test '{0}' is unknown.".format(test)
            sys.exit(1)
            
    # Execute test
    results = {}
    for test in tests:
        results[test] = client.multirun_test(test, args.samples, args.sample_interval)
    output.basic_formating(results)