'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging
import proto
from nsts.tests import base

logger = logging.getLogger("proto")

class NSTSConnectionClient(proto.NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionClient, self).__init__(connection)
    
    def run_test(self, test):
        """
        Execute a complete test on get results back
        """
        
        logger.info("Starting test '{0}'".format(test.friendly_name))

        # ASSURE
        logger.debug("Checking test '{0}'".format(test.name))
        self.assure_test(test.name)
        
        executor = test.client_executor
        assert isinstance(executor, base.TestExecutor)
        
        # PREPARE
        try:
            executor.initialize(self)
            logger.debug("Preparing test '{0}'.".format(test.name))
            self.send_msg("PREPARETEST", {"name" : test.name})
            self.wait_msg_type("OK")
            executor.prepare()
            
            
            # RUN
            logger.debug("Test '{0} started'.".format(test.name))
            executor.run()
                
            # STOP
            logger.debug("Test '{0}' finished.".format(test.name))
            self.send_msg("TESTFINISHED", {"name": test.name})
            self.wait_msg_type("TESTFINISHED")
            
            results = executor.get_results()
        except:
            executor.cleanup()
            raise
        
        #CLEAN UP
        executor.cleanup()
        
        return results
    
class NSTSClient(object):
    
    def __init__(self, remote_host , remote_port = None):
        self.remote_host = remote_host
        self.remote_port = 26532 if remote_port is None else remote_port
        self.connection = None
        self.tests = base.get_enabled_tests()
        
    def connect(self):
        '''
        Connect to the server and start benchmarking
        '''
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.remote_host, self.remote_port))
        except socket.error , msg:
            print 'Connection failed. Error code: ' + str(msg[0]) + 'Error message: ' + msg[1]
            sys.exit()
        
        addr = socket.getaddrinfo(self.remote_host, 0)
        remote_ip = addr[0][4][0]
        self.connection = NSTSConnectionClient(self.socket)
        self.connection.handshake(remote_ip)
        
            
    def run_test(self, test_name):
        return self.connection.run_test(self.tests[test_name])
        