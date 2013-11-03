'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from ntst.proto import Server
import logging

logging.basicConfig(level = logging.DEBUG)

s = Server()
s.serve()