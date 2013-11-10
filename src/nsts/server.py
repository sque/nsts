'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import socket, sys, logging
from nsts import  proto
from nsts.speedtests import base

logger = logging.getLogger("proto")

class NSTSConnectionServer(proto.NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionServer, self).__init__(connection)
    
    def serve_checktest(self, tests, test_id):
        installed = tests.has_key(test_id)
        supported = False
        if installed:
            supported = True # tests[name].server_executor.is_supported()
            logger.warning("FIX ME")
        self.send_msg("TESTINFO",{
                    "test_id" : test_id,
                    "installed" : installed,
                    "supported" : supported,
                    "error" : "unknown"
                    })

    def serve_run_test(self, execution):
        logger.info("Client requested execution of test {0}.".format(execution.name))
        executor = execution.executor
        assert isinstance(executor, base.SpeedTestExecutor)
        
        # PREPARE
        try:
            executor.initialize(self)
            logger.debug("Preparing test '{0}'.".format(execution.name))
            executor.prepare()
            self.send_msg("OK")
            
            # RUN
            logger.debug("Test '{0} started'.".format(execution.name))
            executor.run()
                
            # STOP
            logger.debug("Test '{0}' finished.".format(execution.name))
            self.send_msg("TESTFINISHED", {"execution_id": execution.id})
            self.wait_msg_type("TESTFINISHED")
            
        except Exception, e:
            logger.critical("Unhandled exception: " + str(type(e)) + str(e))
            executor.cleanup()
            raise
        
        executor.cleanup()
        return execution
        
    def process_client_requets(self, tests):
        
        while(True):
            msg = self.wait_msg()
            
            if msg.type == "CHECKTEST":
                self.serve_checktest(tests, msg.params["test_id"])
            elif msg.type == "PREPARETEST":
                test = type(tests[msg.params['test_id']])()
                direction = base.SpeedTestExecutorDirection(msg.params["direction"])
                execution_id = msg.params['execution_id']
                execution = base.SpeedTestExecution(test, direction, execution_id)
                self.serve_run_test(execution)
                
class NSTSServer(object):
    
    def __init__(self, host = None , port = None):
        self.host = '' if host is None else host
        self.port = 26532 if port is None else port
        self.tests = base.get_enabled_tests()

    def serve(self):
        ''' Start the server and start serving
        in the same thread
        '''
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            self.server_socket.bind((self.host, self.port))
        except socket.error , msg:
            print 'Bind failed. Error code: ' + str(msg[0]) + 'Error message: ' + msg[1]
            sys.exit()
        self.server_socket.listen(1)
        logger.info("Server started listening at port {0}".format(self.port))
        print "Server started listening at port {0}".format(self.port)
        # Get new connections loop
        while(True):
            print "Waiting for new connection..."
            (socket_conn, socket_addr) = self.server_socket.accept()
            print 'Got connection from client ' + socket_addr[0] + ':' + str(socket_addr[1])
            try:
                connection = NSTSConnectionServer(socket_conn)
                connection.handshake(socket_addr[0])
                connection.process_client_requets(self.tests)
            except (proto.ConnectionClosedException, socket.error), msg:
                print "Client disconnected."
                