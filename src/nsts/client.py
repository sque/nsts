'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging, time
import proto
from nsts.profiles import base, registry
from nsts.speedtest import SpeedTest, SpeedTestSuite
from nsts.profiles.base import ProfileExecution


logger = logging.getLogger("proto")

class NSTSConnectionClient(proto.NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionClient, self).__init__(connection)
    
    def run_profile(self, execution):
        """
        Execute a complete test on get results back
        """
        assert isinstance(execution, base.ProfileExecution)
        logger.info("Starting test '{0}'".format(execution.name))

        # ASSURE
        logger.debug("Checking test '{0}'".format(execution.name))
        executor = execution.executor
        self.assure_profile(execution.profile.id)
        if not executor.is_supported():
            logger.info("Test '{0}' is not supported.".format(execution.name))
            raise proto.ProtocolError("Test {0} is not supported locally".format(execution.name))
        
        # PREPARE
        try:
            
            logger.debug("Preparing execution '{0}'.".format(execution.name))
            self.send_msg("PREPARETEST", {
                        "profile_id" : execution.profile.id,
                        "direction" : str(execution.direction.opposite()),
                        'execution_id' : execution.id
                        })
            self.wait_msg_type("OK")
            executor.prepare()
            
            # RUN
            logger.debug("Test '{0} started'.".format(execution.name))
            executor.run()
                
            # STOP
            logger.debug("Test '{0}' finished.".format(execution.name))
            self.send_msg("TESTFINISHED", {"execution_id": execution.id})
            self.wait_msg_type("TESTFINISHED")
            
            execution.mark_finished()
        except Exception, e:
            logger.critical("Unhandled exception: " + str(type(e)) + str(e))
            executor.cleanup()
            raise
        
        #CLEAN UP
        executor.cleanup()
        return execution
    
class NSTSClient(object):
    
    def __init__(self, remote_host , remote_port = None):
        self.remote_host = remote_host
        self.remote_port = 26532 if remote_port is None else remote_port
        self.connection = None
        
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
        
            
    def run_profile(self, ctx):
        '''
        Run a profile and return results
        '''
        assert isinstance(ctx, base.ProfileExecution)
        return self.connection.run_profile(ctx)
    
    
    def run_test(self, test, samples, interval):
        '''
        Run a test as described by SpeedTest object
        '''
        assert isinstance(test, SpeedTest)
        
        if test.options['samples'] is not None:
            samples = test.options['samples']
        if test.options['interval'] is not None:
            interval = test.options['interval']
        
        for i in range(0, samples):
            ctx = ProfileExecution(test.profile, test.direction, test.profile_options)
            self.run_profile(ctx)
            test.push_sample(ctx)
            if i < samples -1 and interval.scale('sec') is not None:
                time.sleep(interval.scale('sec'))
    
    def run_suite(self, suite):
        
        assert isinstance(suite, SpeedTestSuite)
        for test in suite.tests:
            self.run_test(test, suite.options['samples'], suite.options['interval'])