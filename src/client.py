'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from nsts.client import NSTSClient
from nsts.tests import *

import logging
logging.basicConfig(level = logging.DEBUG)


c = NSTSClient("localhost")
c.connect()
print "Dummy ", c.run_test("dummy")
print "TCP send ", c.run_test("iperf_tcp_send")
print "TCP receive ", c.run_test("iperf_tcp_receive")