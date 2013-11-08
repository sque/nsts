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
    
    def serve_checktest(self, tests, name):
        installed = tests.has_key(name)
        supported = False
        if installed:
            supported = True # tests[name].server_executor.is_supported()
            logger.warning("FIX ME")
        self.send_msg("TESTINFO",{
                    "name" : name,
                    "installed" : installed,
                    "supported" : supported,
                    "error" : "unknown"
                    })

    def serve_run_test(self, test, direction):
        logger.info("Client requested execution of test {0}.".format(test.friendly_name))
        executor = test.get_executor(direction)
        assert isinstance(executor, base.SpeedTestExecutor)
        
        # PREPARE
        try:
            executor.initialize(self)
            logger.debug("Preparing test '{0}'.".format(test.name))
            executor.prepare()
            self.send_msg("OK")
            
            # RUN
            logger.debug("Test '{0} started'.".format(test.name))
            executor.run()
                
            # STOP
            logger.debug("Test '{0}' finished.".format(test.name))
            self.send_msg("TESTFINISHED", {"name", test.name})
            self.wait_msg_type("TESTFINISHED")
            
            results = executor.get_results()
        except Exception, e:
            logger.critical("Unhandled exception: " + str(type(e)) + str(e))
            executor.cleanup()
            raise
        
        executor.cleanup()
        return results
        
    def process_client_requets(self, tests):
        
        while(True):
            msg = self.wait_msg()
            
            if msg.type_ == "CHECKTEST":
                self.serve_checktest(tests, msg.params["name"])
            elif msg.type_ == "PREPARETEST":
                direction = base.SpeedTestExecutorDirection(msg.params["direction"])
                self.serve_run_test(tests[msg.params['name']].__class__(), direction)
                
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
                