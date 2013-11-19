'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging, time
from proto import NSTSConnection, ProtocolError
from nsts.profiles import base, registry
from nsts.speedtest import SpeedTest, SpeedTestSuite
from nsts.profiles.base import ProfileExecution
from nsts import core

logger = logging.getLogger("proto")

class NotConnectedError(ProtocolError):
    pass
    def __init__(self):
        super(NotConnectedError, self).__init__("Cannot perform action. Client is not connected.")
        
class NSTSClient(object):
    '''
    NSTS client implementation that permits connecting
    to a server and executing suites, tests or profiles
    '''
    
    def __init__(self, remote_host , remote_port = None, ipv6 = False):
        self.remote_host = remote_host
        self.remote_port = core.DEFAULT_PORT if remote_port is None else remote_port
        self.connection = None
        self.ipv6 = ipv6
        
    def connect(self):
        '''
        Perform actual connection to the server
        '''
        if self.ipv6:
            self.socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
        try:
            self.socket.connect((self.remote_host, self.remote_port))
        except socket.error , msg:
            print 'Connection failed. Error code: ' + str(msg[0]) + 'Error message: ' + msg[1]
            sys.exit()
        logger.debug("TCP connection established.")

        remote_ip = self.socket.getpeername()[0]
        self.connection = NSTSConnection(self.socket)
        self.connection.handshake(remote_ip)
    
    def is_connected(self):
        '''
        Check if client is connected
        '''
        return self.connection is not None
    
    def check_profile(self, profile_id):
        '''
        Request other side to assure that a profile is available
        '''
        if not self.is_connected():
            raise NotConnectedError()
            
        self.connection.send_msg("CHECKPROFILE", {"profile_id" :profile_id})
        profile_info = self.connection.wait_msg_type("PROFILEINFO")
        assert profile_info.params["profile_id"] == profile_id
        if not (profile_info.params["installed"] and profile_info.params["supported"]):
            raise ProtocolError("Profile {0} is not supported remotely".format(profile_info.params['error']))
        
    def run_profile(self, ctx, terminal):
        '''
        Run a profile and return results
        '''
        if not self.is_connected():
            raise NotConnectedError()
        
        terminal.profile_execution_started(ctx)
        logger.info("Requested to execute profile '{0}'".format(ctx.name))
        
        assert isinstance(ctx, base.ProfileExecution)
        
        try:
            executor = ctx.executor
            
            # Check support (remote and local
            logger.debug("Checking profile '{0}'".format(ctx.name))
            
            if not executor.is_supported():
                logger.info("Profile '{0}' is not supported locally.".format(executor.name))
                raise ProtocolError("Test {0} is not supported locally".format(ctx.name))
            self.check_profile(ctx.profile.id)

            # Instantiate profile remotely
            logger.debug("Request remote to instantiate profile '{0}'.".format(ctx.name))
            self.connection.send_msg("INSTANTIATEPROFILE", {
                        "profile_id" : ctx.profile.id,
                        "direction" : str(ctx.direction.opposite()),
                        "options" : ctx.options,
                        'execution_id' : ctx.id
                        })
            self.connection.wait_msg_type("OK")
            executor.prepare()
            
            # Execute profile
            logger.debug("Profile execution '{0} started'.".format(ctx.name))
            executor.run()
                
            # Stop execution
            logger.debug("Profile '{0}' finished.".format(ctx.name))
            ctx.connection.send_msg("EXECUTIONFINISHED", {"execution_id": ctx.id})
            ctx.connection.wait_msg_type("EXECUTIONFINISHED")
            
            ctx.mark_finished()
        except BaseException, e:
            logger.critical("Unhandled exception: " + str(type(e)) + str(e))
            executor.cleanup()
            raise
        
        #Clean up
        executor.cleanup()
        terminal.profile_execution_finished(ctx)
    
    
    def run_test(self, test, samples, interval, terminal):
        '''
        Run a test as described by SpeedTest object.
        It will execute profile multiple times and
        save results in the given test parameter.
        @param test SpeedTest object
        @param samples int Default number of samples
        @param interval float Seconds between samples
        @param terminal The terminal to output progress
        '''
        assert isinstance(test, SpeedTest)
        
        terminal.test_execution_started(test)
        
        if test.options['samples'] is not None:
            samples = test.options['samples']
        if test.options['interval'] is not None:
            interval = test.options['interval']
        
        # Run profile multiple times and save results
        for i in range(0, samples):
            
            # Create execution
            ctx = ProfileExecution(
                profile = test.profile,
                direction = test.direction,
                connection = self.connection,
                options = test.profile_options)
            
            self.run_profile(ctx, terminal)
            test.push_sample(ctx)
            
            # Wait if interval is set and it is not last
            if i < samples -1 and interval.scale('sec') is not None:
                time.sleep(interval.scale('sec'))
        terminal.test_execution_finished(test)
    
    def run_suite(self, suite, terminal):
        '''
        Run a SpeedTestSuite
        @param suite The suite to be executed
        @param terminal The terminal to output progress
        '''
        assert isinstance(suite, SpeedTestSuite)
        terminal.suite_execution_started(suite)
        
        for test in suite.tests:
            self.run_test(test, suite.options['samples'], suite.options['interval'], terminal)
        terminal.suite_execution_finished(suite)