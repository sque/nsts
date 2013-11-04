'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from nsts.client import NSTSClient
import logging

logging.basicConfig(level = logging.DEBUG)


c = NSTSClient("localhost")
c.connect()
print "Finished", c.run_test("dummy")