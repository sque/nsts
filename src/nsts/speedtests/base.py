'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, datetime, hashlib, random
from nsts import proto, utils
from nsts.units import TimeUnit

# Module logger
logger = logging.getLogger("test")

class SpeedTestRuntimeError(RuntimeError):
    '''
    Exception to be raised by test when
    it was unable to execute it.
    '''
    
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
        self.__results = None
        
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
        self.__results = results_msg.params['results']
        
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
    
    def store_result(self, name, value):
        '''
        Store a result value in results container
        '''
        if self.__results is None:
            self.__results = {}
        
        if not self.owner.result_descriptors.has_key(name):
            raise LookupError("Cannot store results for an unknown result type")
        assert isinstance(value, self.owner.result_descriptors[name].unit_type)
        self.__results[name] = value
        
    def get_results(self):
        '''
        Get results of the test executor. This function
        returns the value of self.results.
        ''' 
        
        return self.__results

class ResultEntryDescriptor(object):
    '''
    Descriptor for a result entry
    '''
    def __init__(self, name, friendly_name, unit_type):
        self.name = name
        self.friendly_name = friendly_name
        self.unit_type = unit_type

class SpeedTestExecutorDirection(object):
    
    def __init__(self, initial):
        assert initial in ["send", "receive"]
        self.__direction = initial
        
    def __eq__(self, other):
        assert type(other) == type(self)
        return self.__direction == other.__direction
    
    def __ne__(self, other):
        assert type(other) == type(self)
        return self.__direction != other.__direction
    
    def is_send(self):
        return self.__direction == "send"
    
    def is_receive(self):
        return self.__direction == "receive"
    
    def opposite(self):
        if self.is_send():
            return SpeedTestExecutorDirection("receive")
        else:
            return SpeedTestExecutorDirection("send")
        
    def __str__(self):
        return self.__direction
    
    def __repr__(self):
        return self.__direction
class SpeedTest(object):
    '''
    Base class for implementing a test
    '''
    def __init__(self, name, friendly_name, send_executor, receive_executor, result_descriptors):
        self.name = name
        self.friendly_name = friendly_name
        
        assert issubclass(send_executor, SpeedTestExecutor)
        assert issubclass(receive_executor, SpeedTestExecutor)
        assert isinstance(result_descriptors, list)
        self.__send_executor = send_executor(self)
        self.__receive_executor = receive_executor(self)
        self.result_descriptors = {}
        for desc in result_descriptors:
            self.result_descriptors[desc.name] = desc
        
    def initialize(self, local_ip, remote_ip):
        pass
    
    def get_executor(self, direction):
        '''
        Choose executor by specific direction.
        '''
        assert isinstance(direction, SpeedTestExecutorDirection)
        
        if direction.is_send():
            return self.__send_executor
        else:
            return self.__receive_executor
    
class SpeedTestResults(object):
    '''
    Results container of one speedtest execution 
    '''
    
    def __init__(self, test):
        self.test = test
        assert isinstance(self.test, SpeedTest)
        
        self.started_at = datetime.datetime.utcnow()
        self.ended_at = None
        self.values = None
        
        sha1 = hashlib.sha1()
        sha1.update( test.name + str(self.started_at) + str(random.random()))
        self.test_execution_id = sha1.hexdigest()
    
    def mark_test_finished(self, values):
        '''
        Fill end timestamp and save results values in the object
        '''
        assert isinstance(values, dict)
        self.ended_at = datetime.datetime.utcnow()
        self.values = values
    
    def execution_time(self):
        return TimeUnit((self.ended_at - self.started_at).total_seconds())
    
    def __iter__(self):
        return self.values.__iter__()

class SpeedTestMultiSampleResults(SpeedTestResults):
    
    def __init__(self, test):
        super(SpeedTestMultiSampleResults, self).__init__(test)
        del self.values
        self.samples = []
        
    def push_sample(self, sample):
        assert isinstance(sample, SpeedTestResults)
        self.samples.append(sample)
    
    def mark_test_finished(self):
        '''
        Fill end timestamp and save __results in the object
        '''
        self.ended_at = datetime.datetime.utcnow()
        
    def get_statistics(self):
        '''
        Calculate statistics on samples
        '''
        reduced = {}
        for result_entry in self.test.result_descriptors.values():
            assert isinstance(result_entry, ResultEntryDescriptor)
            
            # Collect all samples raw values
            data = utils.StatisticsArray([sample.values[result_entry.name].raw_value for sample in self.samples])
            
            reduced_entry = {
                'mean' :  result_entry.unit_type(data.mean()),
                'min' :  result_entry.unit_type(data.min()),
                'max' :  result_entry.unit_type(data.max()),
                'std' :  result_entry.unit_type(data.std()),
            }
            
            reduced[result_entry.name] = reduced_entry

        return reduced
    
    def __iter__(self):
        return self.samples.__iter__()
    
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


def get_enabled_test(test_name):
    '''
    Get access to a specific test
    '''
    return __enabled_tests[test_name]

def is_test_enabled(test):
    '''
    Check if test is enabled
    '''
    tests = get_enabled_tests()
    
    return test in tests.keys()