#!/usr/bin/env python
'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, argparse, sys
from nsts.client import NSTSClient
from nsts.server import NSTSServer
from nsts.speedtests import *
from nsts.io import formatters
from nsts.io.grid import Grid

parser = argparse.ArgumentParser(
        epilog="This application was developed for the need of "
        "benchmarking wireless links at heraklion wireless "
        "metropolitan network (hwmn.org). If you find a bug please "
        "report it at https://github.com/sque/nsts")
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
    formater = formatters.BasicFormatter()
    
    # List tests mode
    print ""
    print "Installed SpeedTests"
    g = Grid(80)
    g.add_column('ID', width='fit')
    g.add_column('Name')
    g.add_column('Client', width = 'fit', align='center')
    g.add_column('Server', width = 'fit', align='center')
    
    for test in base.get_enabled_tests().values():
        check_mark = lambda b : 'X' if b else '-' 
        g.add_row([test.id,
                test.name,
                'X','X'])#check_mark(test.client_executor.is_supported()),
               # check_mark(test.server_executor.is_supported())])
    print g
    
elif args.server:
    # Server Mode
    server = NSTSServer()
    server.serve()
else:
    formater = formatters.BasicFormatter()
    formater.connection_info(args.samples, args.connect, '?', args.tests)
    
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
    send = base.SpeedTestExecutorDirection('send')
    for test in tests:
        test_result = client.multirun_test(test, send, args.samples, args.sample_interval)
        formater.push_test_results(test_result)
    
    # Finish
    formater.finish()