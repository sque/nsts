'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import subprocess as proc, logging
from nsts import utils, proto

# Module logger
logger = logging.getLogger("test")

class TestExecutor(object):
    '''
    Base class for implementing a peer executor
    '''
    
    def __init__(self, owner):
        assert isinstance(owner, Test)
        self.owner = owner
        self.connection = None
        self.logger = logging.getLogger("test.{0}".format(self.owner.name))
        self.results = None
        
    def initialize(self, connection):
        '''
        Called by the nsts system to initialize executor
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
        raise NotImplementedError()
    
    def prepare(self):
        raise NotImplementedError()
    
    def run(self):
        raise NotImplementedError()
    
    def cleanup(self):
        raise NotImplementedError()
    
    def get_results(self):
        '''
        Get results of the test executor. This function
        returns the value of self.results.
        ''' 
        
        return self.results
class Test(object):
    '''
    Base class for implementing a test
    '''
    def __init__(self, name, friendly_name, client_executor, server_executor):
        self.name = name
        self.friendly_name = friendly_name
        
        assert issubclass(client_executor, TestExecutor)
        assert issubclass(server_executor, TestExecutor)
        self.client_executor = client_executor(self)
        self.server_executor = server_executor(self)

    def initialize(self, local_ip, remote_ip):
        pass

    
# A list with all enabled tests
__enabled_tests = []

def enable_test(test_class):
    '''
    Enable a new test
    '''
    global __enabled_tests
    if test_class not in __enabled_tests:
        __enabled_tests.append(test_class)

def get_enabled_tests():
    '''
    Get a dictionary with instances of all enabled
    tests
    '''
    tests = {}
    for test_class in __enabled_tests:
        test = test_class()
        tests[test.name] = test
        
    return tests