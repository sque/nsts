'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from nsts.proto import Server
import logging

logging.basicConfig(level = logging.DEBUG)

s = Server()
s.serve()