#!/usr/bin/env python
'''
Created on Nov 2, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import logging
import argparse
import sys
from nsts.client import NSTSClient
from nsts.server import NSTSServer
from nsts.profiles import *
from nsts.profiles.base import SpeedTestRuntimeError
from nsts.io import suite
from nsts.io.terminal import BasicTerminal
from nsts import core

from nsts.proto import ProtocolError


def parse_test_arg(name):
    if "-" not in name:
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
    "report it at https://github.com/sque/nsts"
)
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("-c", "--connect", help="connect to server.", type=str)
group.add_argument("-s", "--server", help="start in server mode.",
                   action="store_true")
list_tests = group.add_argument(
    "--list-profiles", help="list all available benchmarking profiles.",
    action="store_true"
)
parser.add_argument(
    "-p", "--port", help="server/client port.",
    type=int, default=core.DEFAULT_PORT
)
parser.add_argument("-d", "--debug", type=int,
                    help="select level of logging. 0 will log everything", )
parser.add_argument("--samples",
                    help="how many times to execute a test (default 1)",
                    default=1, type=int)
parser.add_argument(
    "--interval",
    help="The interval time between samples in seconds. (default 0.0sec)",
    default=0.0, type=float)
parser.add_argument("--log-file",
                    help="file to save logging output", type=str)
group = parser.add_mutually_exclusive_group()
group.add_argument("--tests",
                   help="a comma separated list of all tests to execute")
group.add_argument("--suite",
                   help="a file with a suite to run")
parser.add_argument("-6", "--ipv6",
                    help="use IPv6 protocol for benchmarking",
                    action="store_true")
parser.add_argument(
    "-n", "--numerical-addr",
    help="show numerical addressed, do not try to reverse lookup addresses",
    action="store_true")
parser.add_argument("-v", "--verbose", help="enable verbose output",
                    action="store_true")
args = parser.parse_args()

# Initialize Logging
log_params = {
    'level': logging.INFO if args.log_file else logging.WARNING,
    'format': '%(asctime)s %(levelname)-8s %(name)-15s %(message)s'
    }
if args.log_file:
    log_params['filename'] = args.log_file
if args.debug is not None:
    log_params['level'] = args.debug
logging.basicConfig(**log_params)

# Prepare terminal
terminal = BasicTerminal()
terminal.options['samples'] = args.samples
terminal.options['interval'] = args.interval
terminal.options['verbose'] = args.verbose
terminal.options['suite_filename'] = '' if not args.suite else args.suite
terminal.options['numerical_addr'] = args.numerical_addr

if args.list_profiles:
    terminal.welcome()
    terminal.list_profiles(base.Profile.get_all_profiles().values())
    terminal.epilog()


elif args.server:
    # Server Mode
    server = NSTSServer(ipv6=args.ipv6, port=args.port)
    try:
        server.serve()
    except KeyboardInterrupt:
        pass
    except BaseException, e:
        print "Unknown error"
        print str(e)
else:
    try:
        terminal.welcome()

        # Client Mode
        client = NSTSClient(remote_host=args.connect,
                            remote_port=args.port, ipv6=args.ipv6)
        client.connect()

        terminal.client_connected(client.connection)

        # Load a suite from command line or file
        if args.tests is not None:
            spsuite = suite.parse_command_line(args.tests)
            spsuite.options['samples'] = args.samples
            spsuite.options['interval'] = args.interval
        elif args.suite is not None:
            try:
                spsuite = suite.load_file(args.suite)
            except Exception, e:
                print "Error loading suite file."
                print str(e)
                sys.exit(1)
        else:
            print "You need to define tests or load suite."
            sys.exit(1)

        # Execute suite
        client.run_suite(spsuite, terminal)

        # Finish
        terminal.epilog()
    except (SpeedTestRuntimeError, ProtocolError), e:
        print "Error while executing speedtest suite:"
        print str(e)
        sys.exit(-1)
    except KeyboardInterrupt:
        sys.exit(-1)
    except KeyError, e:
        print 'Unknown value {0}'.format(str(e))
        sys.exit(-2)
    except BaseException, e:
        print "Unknown error: ", str(e)
        sys.exit(-3)