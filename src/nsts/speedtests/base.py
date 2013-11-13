'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, datetime, hashlib, random
from collections import OrderedDict
from nsts import proto, utils
from nsts.units import TimeUnit, Unit

# Module logger
logger = logging.getLogger("test")

class SpeedTestRuntimeError(RuntimeError):
    '''
    Exception to be raised by test when
    it was unable to execute it.
    '''

class ResultValueDescriptor(object):
    '''
    Descriptor of test result entry
    '''
    def __init__(self, result_id, name, unit_type):
        if not issubclass(unit_type, Unit):
            raise TypeError("unit_type must be of units.Unit")

        self.__id = result_id
        self.__name = name
        self.__unit_type = unit_type

    @property
    def id(self):
        '''
        Get the id of this result
        '''
        return self.__id
    
    @property
    def name(self):
        '''
        Get a friendly name of this entry
        '''
        return self.__name
    
    @property
    def unit_type(self):
        '''
        Get the unit type of this entry
        '''
        return self.__unit_type

class OptionValueDescriptor(object):
    '''
    Descriptor of test option value
    '''
    def __init__(self, option_id, help, type):
        assert isinstance(help, basestring)
        self.__id = str(option_id)
        self.__help = help
        self.__type = type
    
    @property
    def id(self):
        '''
        Get the id of this option
        '''
        return self.__id
    
    @property
    def help(self):
        '''
        Get a help string, describing usage of this option
        '''
        return self.__help
    
    @property
    def type(self):
        '''
        Get the type of this option
        '''
        return self.__type


class ExecutionDirection(object):
    '''
    Encapsulates the logic of data direction in execution.
    '''
    
    def __init__(self, direction):
        '''
        Create an initialized object
        @param direction A string 'send','s',receive' or 'r' for the
        state of this object.
        '''
        if direction in ['send', 's']:
            self.__direction = 'send'
        elif direction in ['receive', 'r']:
            self.__direction = 'receive'
        else:
            raise ValueError("Direction '{0}' is not a valid direction.".format(direction))
    
    def is_send(self):
        '''
        Check if it is sending direction
        '''
        return self.__direction == "send"
    
    def is_receive(self):
        '''
        Check if it is receiving direction
        '''
        return self.__direction == "receive"
    
    def opposite(self):
        '''
        Get ExecutionDirection object of the
        opposite direction.
        '''
        if self.is_send():
            return self.__class__("receive")
        else:
            return self.__class__("send")
    
    def __eq__(self, other):
        assert type(other) == type(self)
        return self.__direction == other.__direction
    
    def __ne__(self, other):
        assert type(other) == type(self)
        return self.__direction != other.__direction
    
    def __str__(self):
        return self.__direction
    
    def __repr__(self):
        return self.__direction

class SpeedTestExecutor(object):
    '''
    Base class for implementing a peer executor
    '''
    
    def __init__(self, owner):
        '''
        @param owner The owner SpeedTestDescriptor of this executor
        '''
        if not isinstance(owner, SpeedTestDescriptor):
            raise TypeError("Owner is not of 'SpeedTestDescriptor' type")
        self.__owner = owner
        self.__results = OrderedDict()
        for rid in self.owner.supported_results.keys():
            self.__results[rid] = None
        self.__connection = None
        self.logger = logging.getLogger("test.{0}".format(self.owner.name))
    
    @property
    def owner(self):
        '''
        Get SpeedTestDecriptor Owner of this executor instance
        '''
        return self.__owner

    @property
    def results(self):
        '''
        Get results of the test executor. This function
        returns the value of self.results.
        ''' 
        return self.__results
    
    @property
    def connection(self):
        '''
        Get the connection object that will be used
        by this executor.
        '''
        return self.__connection
    
    def initialize(self, connection):
        '''
        Called by the NSTS system to initialize executor
        @param connection The NSTSConnectionBase object that
        can be used to communicate with the other executor.
        '''
        self.__connection = connection
        assert isinstance(self.connection, proto.NSTSConnectionBase)
    
    def send_msg(self, msg_type, msg_params = {}):
        '''
        Wrapper for sending messages in the way that protocol
        defines intra-test communication.
        '''
        return self.connection.send_msg("__{0}_{1}".format(self.owner.id, msg_type), msg_params)
    
    def wait_msg_type(self, expected_type):
        '''
        Wrapper for receiving messages in the way that protocol
        defines intra-test communication.
        '''
        return self.connection.wait_msg_type("__{0}_{1}".format(self.owner.id, expected_type))
    
    def store_result(self, result_id, value):
        '''
        Store a result value in results container
        '''
        if not self.__results.has_key(result_id):
            raise ValueError("Cannot store results for unknown result id '{0}'".format(result_id))
        self.__results[result_id] = self.owner.supported_results[result_id].unit_type(value)
    
    def propagate_results(self):
        '''
        Propagate results to the other executors
        '''
        self.send_msg("RESULTS", {"results" : self.results})
        
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
    

class SpeedTestDescriptor(object):
    '''
    A SpeedTest descriptor, is used to describe
    a speedtest operation model.
    '''
    
    def __init__(self, test_id, name, send_executor_class, receive_executor_class):
        if not issubclass(send_executor_class, SpeedTestExecutor) or \
            not issubclass(receive_executor_class, SpeedTestExecutor):
            raise TypeError("executor_class must be subclass of SpeedTestExecutor")
        self.__test_id = test_id
        self.__name = name
        self.__send_executor_class = send_executor_class
        self.__receive_executor_class = receive_executor_class
        self.__result_descriptors = OrderedDict()
        self.__options_descriptors = OrderedDict()
    
    @property
    def id(self):
        '''
        Get the id of Test
        '''
        return self.__test_id
    
    @property
    def name(self):
        '''
        Get the name of the test
        '''
        return self.__name
    
    @property
    def send_executor_class(self):
        '''
        Type of the send executor
        '''
        return self.__send_executor_class
    
    @property
    def receive_executor_class(self):
        '''
        Type of the receive executor object
        '''
        return self.__receive_executor_class

    @property
    def supported_results(self):
        '''
        Get a list with all supported results entries
        '''
        return self.__result_descriptors
    
    @property
    def supported_options(self):
        '''
        Get a list with all supported options
        '''
        return self.__options_descriptors
    
    def add_result(self, value_id, name, unit_type):
        '''
        Declare a supported result entry
        @param value_id The identifier of this result value
        @param name A friendly name of this result value
        @param unit_type The type of this result value
        '''
        self.__result_descriptors[value_id] = ResultValueDescriptor(value_id, name, unit_type)

    def add_option(self, option_id, help, unit_type):
        '''
        Declare a supported option for the test
        @param option_id The identifier of the option
        @param help A help string for the end user
        @param unit_type The type of this value
        '''
        self.__supported_options[option_id] = OptionValueDescriptor(option_id, help, unit_type)

    def executor(self, direction):
        '''
        Get a new executor instance based on direction
        '''
        assert isinstance(direction, ExecutionDirection)
        
        if direction.is_send():
            return self.__send_executor_class(self)
        else:
            return self.__receive_executor_class(self)

class SpeedTestExecution(object):
    '''
    Speedtest execution context
    '''
    
    def __init__(self, test, direction, execution_id = None):
        '''
        @param test The SpeedTest object to execute
        @param direction The direction of test execution
        @param execution_id If it is empty, a new one will be generated
        '''
        assert isinstance(test, SpeedTestDescriptor)
        assert isinstance(direction, ExecutionDirection)
        
        self.__test = test
        self.__direction = direction
        
        self.started_at = datetime.datetime.utcnow()
        self.ended_at = None
        
        # Generate execution id
        if execution_id is None:
            sha1 = hashlib.sha1()
            sha1.update( test.id + str(self.started_at) + str(random.random()))
            self.__execution_id = sha1.hexdigest()
        else:
            self.__execution_id = execution_id
    
    @property
    def id(self):
        '''
        Get the execution id of speedtest
        '''
        return self.__execution_id
    
    @property
    def test(self):
        '''
        Get test object that was used for this execution
        '''
        return self.__test
    
    @property
    def direction(self):
        '''
        Get direction that test was executed
        '''
        return self.__direction
    
    @property
    def name(self):
        '''
        Get name of this execution
        '''
        return "{0} - {1}".format(self.test.name, str(self.direction))
    
    @property
    def executor(self):
        '''
        Get executor for this execution
        '''
        return self.test.executor(self.direction)
    
    @property
    def results(self):
        '''
        Get results of this execution
        '''
        return self.executor.results
    
    def mark_finished(self):
        '''
        Fill end timestamp and save results values in the object
        '''
        self.ended_at = datetime.datetime.utcnow()
    
    def execution_time(self):
        return TimeUnit((self.ended_at - self.started_at).total_seconds())
    
    def __iter__(self):
        return self.results.__iter__()


class SpeedTestMultiSampleExecution(object):
    '''
    Pack of multiple SpeedTestExecution objects
    '''
    def __init__(self, test, direction):
        assert isinstance(test, SpeedTestDescriptor)
        assert isinstance(direction, ExecutionDirection)

        self.__test = test
        self.__direction = direction
        self.samples = []

    @property
    def test(self):
        '''
        Get test object that was used for this execution
        '''
        return self.__test
    
    @property
    def direction(self):
        '''
        Get direction that test was executed
        '''
        return self.__direction
    
    @property
    def started_at(self):
        '''
        Get when was the first sample executed.
        '''
        return self.samples[0].started_at
    
    def push_sample(self, sample):
        '''
        Push another sample in the execution list
        '''
        assert isinstance(sample, SpeedTestExecution)
        self.samples.append(sample)
    
    def statistics(self):
        '''
        Calculate statistics on samples
        '''
        reduced = {}
        for result_entry in self.test.result_descriptors.values():
            assert isinstance(result_entry, ResultValueDescriptor)
            
            # Collect all samples raw values
            data = utils.StatisticsArray([sample.results[result_entry.name].raw_value for sample in self.samples])
            
            reduced_entry = {
                'mean' :  result_entry.unit_type(data.mean()),
                'min' :  result_entry.unit_type(data.min()),
                'max' :  result_entry.unit_type(data.max()),
                'std' :  result_entry.unit_type(data.std()),
            }
            
            reduced[result_entry.name] = reduced_entry

        return reduced
    
    def execution_time(self):
        '''
        Get total execution time for all samples
        '''
        return sum([s.execution_time() for s in self.samples], TimeUnit(0))
    
    def __iter__(self):
        return self.samples.__iter__()

