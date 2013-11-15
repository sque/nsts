'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging
from nsts import proto, core
from nsts.speedtest import SpeedTest, SpeedTestSuite
from nsts.profiles import registry
from nsts.profiles.base import ExecutionDirection, ProfileExecution
from nsts.proto import NSTSConnection

logger = logging.getLogger("proto")

class NSTSServer(object):
    '''
    NSTS server implementation that permits serial
    serving of clients to execute their profiles.
    '''
    
    def __init__(self, host = None , port = None):
        self.host = '' if host is None else host
        self.port = core.DEFAULT_PORT if port is None else port

    def __serve_cmd_checkprofile(self, connection, test_id):
        '''
        Serve client command of checking profile status
        '''
        installed = registry.is_registered(test_id)
        supported = False
        if installed:
            supported = True 
            logger.warning("FIX ME: supported")
        
        connection.send_msg("PROFILEINFO",{
                    "profile_id" : test_id,
                    "installed" : installed,
                    "supported" : supported,
                    "error" : "unknown"
                    })
    
    def __serve_cmd_run_profile(self, ctx):
        '''
        Serve client command of executing a profile
        '''
        logger.info("Client requested execution of profile {0}.".format(ctx.name))
        
        try:
            executor = ctx.executor
            logger.debug("Preparing profile '{0}'.".format(ctx.name))
            executor.prepare()
            ctx.connection.send_msg("OK")
            
            # RUN
            logger.debug("Profile '{0}' started.".format(ctx.name))
            executor.run()
                
            # STOP
            logger.debug("Test '{0}' finished.".format(ctx.name))
            ctx.connection.send_msg("EXECUTIONFINISHED", {"execution_id": ctx.id})
            ctx.connection.wait_msg_type("EXECUTIONFINISHED")
            
        except Exception, e:
            logger.critical("Unhandled exception: " + str(type(e)) + str(e))
            executor.cleanup()
            raise
        
        executor.cleanup()
    
    def __cmd_dispatcher(self, connection):
        '''
        Read messages from client and dispatch
        to different commands
        '''
        while(True):
            
            msg = connection.wait_msg()
            
            if msg.type == "CHECKPROFILE":
                # Check a profile
                self.__serve_cmd_checkprofile(connection, msg.params["profile_id"])
                
            elif msg.type == "INSTANTIATEPROFILE":
                # Run a profile
                profile = registry.get_profile(msg.params['profile_id'])
                direction = ExecutionDirection(msg.params["direction"])
                execution_id = msg.params['execution_id']
                options = msg.params['options']
                
                execution = ProfileExecution(
                        profile,
                        direction,
                        options,
                        connection,
                        execution_id)
                
                self.__serve_cmd_run_profile(execution)
                
    def serve(self):
        ''' Start the server and start serving serially
        in the same thread.
        '''
        
        # Create socket
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(1)
        except socket.error , msg:
            print 'Socket error.. Error code: ' + str(msg[0]) + 'Error message: ' + msg[1]
            sys.exit()
        
        logger.info("Server started listening at port {0}".format(self.port))
        print "Server started listening at port {0}".format(self.port)

        # Get new connections loop
        while(True):
            print "Waiting for new connection..."
            (socket_conn, socket_addr) = self.server_socket.accept()
            print 'Got connection from client ' + socket_addr[0] + ':' + str(socket_addr[1])
            try:
                connection = NSTSConnection(socket_conn)
                connection.handshake(socket_addr[0])
                self.__cmd_dispatcher(connection)
            except (proto.ConnectionClosedException, socket.error), msg:
                print "Client disconnected."
                