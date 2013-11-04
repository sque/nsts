#!/usr/bin/env python
'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, argparse
from nsts.client import NSTSClient
from nsts.server import NSTSServer
from nsts.tests import *

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-c", "--connect", help="connect to server.", type=str)
group.add_argument("-s","--server", help="start in server mode.", action="store_true")
group.add_argument("--list-tests", help="list all available tests.", action="store_true")
parser.add_argument("-d", "--debug", 
                    help="select level of logging. 0 will log everyting", 
                    type=int, default = logging.WARNING)
args = parser.parse_args()

# Prepare logging
logging.basicConfig(level = args.debug)

if args.list_tests:
    print "Tests currently installed "
    print "-------------------------"
    for test in base.get_enabled_tests().values():
        print " * [{0}] {1}".format(test.name, test.friendly_name)
elif args.server:
    server = NSTSServer()
    server.serve()
else:
    client = NSTSClient(args.connect)
    client.connect()
    print "Dummy ", client.run_test("dummy")
    print "TCP send ", client.run_test("iperf_tcp_send")
    print "TCP receive ", client.run_test("iperf_tcp_receive")