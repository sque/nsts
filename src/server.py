'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from nsts.server import NSTSServer
from nsts.tests import *

import logging

logging.basicConfig(level = logging.DEBUG)

s = NSTSServer()
s.serve()