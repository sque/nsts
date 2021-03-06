'''
Created on Nov 12, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import unittest
from nsts.io.suite import parse_command_line
from nsts.profiles import *


class TestParseCommandLine(unittest.TestCase):

    def test_one_bidirectional(self):
        line = "dummy"

        suite = parse_command_line(line)
        self.assertEqual(['dummy', 'dummy'],
                         [t.profile.id for t in suite.tests])
        self.assertEqual(['send', 'receive'],
                         [str(t.direction) for t in suite.tests])

    def test_one_send(self):
        line = "dummy-s"

        suite = parse_command_line(line)
        self.assertEqual(['dummy'], [t.profile.id for t in suite.tests])
        self.assertEqual(['send'], [str(t.direction) for t in suite.tests])

    def test_one_receive(self):
        line = "dummy-r"

        suite = parse_command_line(line)
        self.assertEqual(['dummy'], [t.profile.id for t in suite.tests])
        self.assertEqual(['receive'], [str(t.direction) for t in suite.tests])

    def test_multi(self):
        line = "dummy-r,dummy-s,iperf_tcp-s,iperf_jitter-r"

        suite = parse_command_line(line)
        self.assertEqual(['dummy', 'dummy', 'iperf_tcp', 'iperf_jitter'],
                         [t.profile.id for t in suite.tests])
        self.assertEqual(['receive', 'send', 'send', 'receive'],
                         [str(t.direction) for t in suite.tests])
