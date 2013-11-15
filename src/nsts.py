#!/usr/bin/env python
'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, argparse, sys
from nsts.client import NSTSClient
from nsts.server import NSTSServer
from nsts.profiles import *
from nsts.profiles import registry
from nsts.io import suite
from nsts.io.grid import Grid
from nsts.io.terminal import BasicTerminal
from nsts import units, core


def parse_test_arg(name):
    if not "-" in name:
        return [
                (name, base.ExecutionDirection("send")),
                (name, base.ExecutionDirection("receive"))
                ]
    parts = name.split("-")
    test_name = parts[0]
    if parts[1] not in ["s", "r"]:
        raise RuntimeError("Test directive can be 'r' or 's'.")
    
    if parts[1] == 's':
        test_dir = base.ExecutionDirection("send")
    else:
        test_dir = base.ExecutionDirection("receive")
    
    return [(test_name, test_dir)]
    
parser = argparse.ArgumentParser(
        epilog="This application was developed for the need of "
        "benchmarking wireless links at heraklion wireless "
        "metropolitan network (hwmn.org). If you find a bug please "
        "report it at https://github.com/sque/nsts")
group = parser.add_mutually_exclusive_group(required = True)
group.add_argument("-c", "--connect", help="connect to server.", type=str)
group.add_argument("--port", help="server port.", type=int, default=core.DEFAULT_PORT)
group.add_argument("-s","--server", help="start in server mode.", action="store_true")
list_tests = group.add_argument("--list-profiles", help="list all available benchmarking profiles.", action="store_true")
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
parser.add_argument("-v", "--verbose", help="enable verbose output", action="store_true")
args = parser.parse_args()

# Prepare logging
logging.basicConfig(level = args.debug)

# Prepare terminal
terminal = BasicTerminal()
terminal.options['samples'] = args.samples
terminal.options['interval'] = args.sample_interval
terminal.options['verbose'] = args.verbose

if args.list_profiles:
    terminal.welcome()
    
    # List tests mode
    print ""
    print "Installed Profiles"
    g = Grid(80)
    g.add_column('ID', width='fit')
    g.add_column('Name')
    g.add_column('Client', width = 'fit', align='center')
    g.add_column('Server', width = 'fit', align='center')
    
    for test in registry.get_all():
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
    terminal.options['host'] = args.connect
    terminal.options['port'] = args.port
    terminal.welcome()
    
    # Client Mode
    client = NSTSClient(args.connect, args.port)
    client.connect()
    terminal.client_connected()
    
    # Load a suite from command line or file
    spsuite = suite.parse_command_line(args.tests)
    spsuite.options['samples'] = args.samples
    spsuite.options['interval'] = args.sample_interval
    
    # Execute suite
    client.run_suite(spsuite, terminal)
    
    
    # Finish
    terminal.epilog()