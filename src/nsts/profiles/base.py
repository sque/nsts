'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import logging, datetime, hashlib, random
from collections import OrderedDict
from nsts.proto import NSTSConnection
from nsts.units import TimeUnit, Unit
from nsts.options import OptionsDescriptor, Options

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

class ProfileExecutor(object):
    '''
    Base class for implementing a profile peer executor
    '''
    
    def __init__(self, context):
        '''
        @param context The execution context
        '''
        if not isinstance(context, ProfileExecution):
            raise TypeError("{0} is not instance of ProfileExecution".format(context))
        
        self.__execution_ctx = context
        self.logger = logging.getLogger("profile.{0}".format(self.profile.id)) 
        self.__results = OrderedDict()
        for rid in self.profile.supported_results.keys():
            self.__results[rid] = None
        
    @property
    def profile(self):
        '''
        Get Profile owner of this executor instance
        '''
        return self.context.profile

    @property
    def results(self):
        '''
        Get results of the test executor. This function
        returns the value of self.results.
        ''' 
        return self.__results
    
    @property
    def context(self):
        '''
        Get the execution context for this executor instance
        '''
        return self.__execution_ctx
    
    def send_msg(self, msg_type, msg_params = {}):
        '''
        Wrapper for sending messages in the way that protocol
        defines intra-test communication.
        '''
        return self.context.connection.send_msg("__{0}_{1}".format(self.profile.id, msg_type), msg_params)
    
    def wait_msg_type(self, expected_type):
        '''
        Wrapper for receiving messages in the way that protocol
        defines intra-test communication.
        '''
        return self.context.connection.wait_msg_type("__{0}_{1}".format(self.profile.id, expected_type))
    
    def store_result(self, result_id, value):
        '''
        Store a result value in results container
        '''
        if not self.__results.has_key(result_id):
            raise ValueError("Cannot store results for unknown result id '{0}'".format(result_id))
        self.__results[result_id] = self.profile.supported_results[result_id].unit_type(value)
    
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
    

class Profile(object):
    '''
    A Profile describes a benchmark tool. It holds
    information about options and results and scripts
    that invoke the test.
    '''
    
    def __init__(self, test_id, name, send_executor_class, receive_executor_class, description = None):
        if not issubclass(send_executor_class, ProfileExecutor) or \
            not issubclass(receive_executor_class, ProfileExecutor):
            raise TypeError("executor_class must be subclass of ProfileExecutor")
        self.__test_id = test_id
        self.__name = name
        self.__send_executor_class = send_executor_class
        self.__receive_executor_class = receive_executor_class
        self.__supported_results = OrderedDict()
        self.__supported_options = OptionsDescriptor()
        self.__description = description
    
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
    def description(self):
        '''
        Get a description of the profile
        '''
        return self.__description
    
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
        return self.__supported_results
    
    @property
    def supported_options(self):
        '''
        Get a list with all supported options
        '''
        return self.__supported_options
    
    def add_result(self, value_id, name, unit_type):
        '''
        Declare a supported result entry
        @param value_id The identifier of this result value
        @param name A friendly name of this result value
        @param unit_type The type of this result value
        '''
        self.__supported_results[value_id] = ResultValueDescriptor(value_id, name, unit_type)

class ProfileExecution(object):
    '''
    Execution context for a single speedtest profile
    '''
    
    def __init__(self, profile, direction, options, connection, execution_id = None):
        '''
        @param profile The Profile object to execute
        @param direction The direction of test execution
        @param execution_id If it is empty, a new one will be generated
        '''
        if not isinstance(profile, Profile):
            raise TypeError("{0} is not an instance of Profile".format(profile))
        if not isinstance(direction, ExecutionDirection):
            raise TypeError("{0} is not an instance of ExecutionDirection".format(direction))
        if not isinstance(options, Options):
            raise TypeError("{0} is not an instance of Options".format(options))
        if not isinstance(connection, NSTSConnection):
            raise TypeError("{0} is not an instance of NSTSConnection".format(connection))
        
        self.__profile = profile
        self.__direction = direction
        self.__options = options
        self.__connection = connection
        
        self.started_at = datetime.datetime.utcnow()
        self.ended_at = None
        
        # Generate execution id
        if execution_id is None:
            sha1 = hashlib.sha1()
            sha1.update(profile.id + str(self.started_at) + str(random.random()))
            self.__execution_id = sha1.hexdigest()
        else:
            self.__execution_id = execution_id
        
        # Create executor
        if self.direction.is_send():
            self.__executor = self.profile.send_executor_class(self)
        else:
            self.__executor = self.profile.receive_executor_class(self)

    
    @property
    def id(self):
        '''
        Get the execution id of speedtest
        '''
        return self.__execution_id
    
    @property
    def options(self):
        '''
        Get options for the executor
        '''
        return self.__options
    
    @property
    def profile(self):
        '''
        Get profile that was used for this execution
        '''
        return self.__profile
    
    @property
    def direction(self):
        '''
        Get direction that test was executed
        '''
        return self.__direction
    
    @property
    def connection(self):
        '''
        Get connection object
        '''
        return self.__connection
    
    @property
    def name(self):
        '''
        Get name of this execution
        '''
        return "{0} - {1}".format(self.profile.name, str(self.direction))
    
    @property
    def executor(self):
        '''
        Get executor of this context
        '''
        return self.__executor
    
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

