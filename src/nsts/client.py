'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging, time
import proto
from nsts.speedtests import base, registry


logger = logging.getLogger("proto")

class NSTSConnectionClient(proto.NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionClient, self).__init__(connection)
    
    def run_test(self, execution):
        """
        Execute a complete test on get results back
        """
        assert isinstance(execution, base.SpeedTestExecution)
        logger.info("Starting test '{0}'".format(execution.name))

        # ASSURE
        logger.debug("Checking test '{0}'".format(execution.name))
        executor = execution.executor
        assert isinstance(executor, base.SpeedTestExecutor)
        self.assure_test(execution.test.id)
        if not executor.is_supported():
            logger.info("Test '{0}' is not supported.".format(execution.name))
            raise proto.ProtocolError("Test {0} is not supported locally".format(execution.name))
        
        # PREPARE
        try:
            
            executor.initialize(self)
            logger.debug("Preparing execution '{0}'.".format(execution.name))
            self.send_msg("PREPARETEST", {
                        "test_id" : execution.test.id,
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
        
            
    def run_test(self, test_id, direction):
        '''
        Run a test and return results
        '''
        ctx = base.SpeedTestExecution(registry.get_test(test_id), direction)
        return self.connection.run_test(ctx)
    
    
    def multirun_test(self, test_id, direction, times, interval_secs = None):
        '''
        Run a test multiple times between intervals and return results
        '''
        results = base.SpeedTestMultiSampleExecution(registry.get_test(test_id), direction)
        
        for i in range(0, times):
            execution = self.run_test(test_id, direction)
            results.push_sample(execution)
            if i < times -1 and interval_secs is not None:
                time.sleep(interval_secs)
        return results