'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, datetime, hashlib, random
from nsts import proto

# Module logger
logger = logging.getLogger("test")

class SpeedTestExecutor(object):
    '''
    Base class for implementing a peer executor
    '''
    
    def __init__(self, owner):
        '''
        @param owner The owner SpeedTest of this executor
        '''
        assert isinstance(owner, SpeedTest)
        self.owner = owner
        self.connection = None
        self.logger = logging.getLogger("test.{0}".format(self.owner.name))
        self.results = None
        
    def initialize(self, connection):
        '''
        Called by the NSTS system to initialize executor
        @param connection The NSTSConnectionBase object that
        can be used to communicate with the other executor.
        '''
        self.connection = connection
        assert isinstance(self.connection, proto.NSTSConnectionBase)
    
    def send_msg(self, msg_type, msg_params = {}):
        '''
        Wrapper for sending messages in the way that protocol
        defines inter-test communication.
        '''
        return self.connection.send_msg("__{0}_{1}".format(self.owner.name, msg_type), msg_params)
    
    def wait_msg_type(self, expected_type):
        '''
        Wrapper for receiving messages in the way that protocol
        defines inter-test communication.
        '''
        return self.connection.wait_msg_type("__{0}_{1}".format(self.owner.name, expected_type))
    
    def propagate_results(self):
        '''
        Propagate results to the other executors
        '''
        self.send_msg("RESULTS", {"results" : self.get_results()})
        
    def collect_results(self):
        '''
        Collect results that where propagated by the other
        executor.
        '''
        results_msg = self.wait_msg_type("RESULTS")
        self.results = results_msg.params['results']
        
    def is_supported(self):
        '''
        The executor should check if it supported
        by the current system and return a boolean flag.
        '''
        raise NotImplementedError()
    
    def prepare(self):
        '''
        Prepare executor for running the test
        '''
        raise NotImplementedError()
    
    def run(self):
        '''
        Implemented by executor and involves all the testing
        procedure. It is up to the executor to synchronize
        and controll the running loop of the other-end executor.
        '''
        raise NotImplementedError()
    
    def cleanup(self):
        '''
        Called when test is stopped or crashed. The executor
        should do any needed cleanup
        '''
        raise NotImplementedError()
    
    def get_results(self):
        '''
        Get results of the test executor. This function
        returns the value of self.results.
        ''' 
        
        return self.results

class SpeedTest(object):
    '''
    Base class for implementing a test
    '''
    def __init__(self, name, friendly_name, client_executor, server_executor):
        self.name = name
        self.friendly_name = friendly_name
        
        assert issubclass(client_executor, SpeedTestExecutor)
        assert issubclass(server_executor, SpeedTestExecutor)
        self.client_executor = client_executor(self)
        self.server_executor = server_executor(self)

    def initialize(self, local_ip, remote_ip):
        pass

class SpeedTestResults(object):
    '''
    Wrapper class to hold test results
    '''
    
    def __init__(self, test):
        self.test = test
        assert isinstance(self.test, SpeedTest)
        
        self.started_at = datetime.datetime.utcnow()
        self.ended_at = None
        self.results = None
        
        sha1 = hashlib.sha1()
        sha1.update( test.name + str(self.started_at) + str(random.random()))
        self.test_execution_id = sha1.hexdigest()
    
    def mark_test_finished(self, results):
        '''
        Fill end timestamp and save results in the object
        '''
        self.ended_at = datetime.datetime.utcnow()
        self.results = results
    
    def get_total_seconds(self):
        return (self.ended_at - self.started_at).total_seconds()

# A list with all enabled tests
__enabled_tests = {}

def enable_test(test_class):
    '''
    Enable a new test
    '''
    global __enabled_tests
    if test_class not in __enabled_tests:
        test = test_class()
        __enabled_tests[test.name] = test

def get_enabled_tests():
    '''
    Get a dictionary with instances of all enabled
    tests
    '''
    return __enabled_tests


def is_test_enabled(test):
    '''
    Check if test is enabled
    '''
    tests = get_enabled_tests()
    
    return test in tests.keys()