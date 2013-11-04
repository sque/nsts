'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from nsts.proto import Client
import logging

logging.basicConfig(level = logging.DEBUG)


c = Client("localhost")
c.connect()
print "Finished", c.run_test("iperf")