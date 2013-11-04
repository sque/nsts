'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import socket, sys, pickle, base64, time, logging
import test

# PROTOCOL VERSION
VERSION = 0

# Module logger
logger = logging.getLogger("proto")

class ConnectionClosedException(Exception):
    '''
    Exception to be raised when connection is closed
    '''
    pass

class ProtocolError(Exception):
    '''
    Exception raised on protocol errors.
    '''
    pass

class Message(object):
    '''
    Class to encode and decode messages that
    are exchanged on network
    '''
    def __init__(self, type_, params):
        self.type_ = type_
        self.params = params
    
    def encode(self):
        '''
        Encode this message to a plain text format
        '''
        encoded_params = base64.b64encode(pickle.dumps(self.params))
        return "{0} {1}".format(self.type_, encoded_params)
    
    @staticmethod
    def decode(raw_msg):
        msg_parts = raw_msg.split(" ")
        try:
            msg_params = pickle.loads(base64.b64decode(msg_parts[1]))
        except:
            raise ProtocolError("Error decoding message parameters.")
        return Message(msg_parts[0], msg_params)
    
    def __str__(self):
        return "[{0} {1}]".format(self.type_, self.params)
     
    def __repr__(self):
        return self.__str__
    
    
class MessageStream(object):
    '''
    Wrapper for exchanging plain-text messages over
    sockets.
    '''
    
    MSG_DELIMITER = "\n"
    
    def __init__(self, connection):
        self.connection = connection
        self.receiver_buffer = ''
    
    
    def __buffer_pop_msg(self):
        '''
        Pop a message from the buffer.
        @return None if no messages exists
        '''
        
        end_msg_pos = self.receiver_buffer.find(MessageStream.MSG_DELIMITER)
        if end_msg_pos == -1:
            return None # No line in buffer
        
        # Extract line
        raw_msg = self.receiver_buffer[:end_msg_pos]
        
        # Remove it from buffer
        self.receiver_buffer = self.receiver_buffer[end_msg_pos + len(MessageStream.MSG_DELIMITER):]
        if not raw_msg:
            return None # Drop empty messages
        
        # Decode message
        return Message.decode(raw_msg)
        
    
    def __buffer_push_data(self, data):
        '''
        Push raw data at the buffer
        @param data The data as received from the connection
        '''
        self.receiver_buffer = self.receiver_buffer + data 
        
    def wait_msg(self):
        '''
        Read a message from the connection(blocking).
        '''
        
        # First check the buffer if something exists there
        msg = self.__buffer_pop_msg()
        if msg is not None:
            return msg
        
        # Read new data
        while(True):
            data = self.connection.recv(1024)
            if not data:
                raise ConnectionClosedException()
            self.__buffer_push_data(data)
            msg = self.__buffer_pop_msg()
            if msg is not None:
                logger.debug("Received message {0}".format(msg))
                return msg

    def wait_msg_type(self, expected_type):
        logger.debug("Waiting for '{0}' message".format(expected_type))
        msg = self.wait_msg()
        
        if msg.type_ != expected_type:
            logger.debug("Waiting for '{0}' message, but '{1}' arrived".format(msg.type_, expected_type))
            raise ProtocolError("Waiting for '{0}' message, but '{1}' arrived".format(msg.type_, expected_type))
        return msg
    
    def send_msg(self, msg_type, msg_params = {}):
        '''
        Send a message to the other end.
        '''
        msg = Message(msg_type, msg_params)
        self.connection.send(msg.encode() + MessageStream.MSG_DELIMITER)
        
        
class NSTSConnectionBase(MessageStream):
    '''
    Implement NSTS connection base
    '''
    
    def __init__(self, connection):
        super(NSTSConnectionBase, self).__init__(connection)
        self.remote_ip = None
        self.local_ip = None
        
    def handshake(self, remote_ip):
        '''
        Handshake between two peers.
        In this process, they will validate version compatibility
        and will exchange needed information.
        '''
        self.remote_ip = remote_ip
        self.send_msg('HELLO', {"version" : VERSION, "remote_ip": remote_ip})
        response = self.wait_msg_type('HELLO')
        
        if response.params['version'] != VERSION:
            raise ProtocolError("Incompatible version")
        self.local_ip = response.params['remote_ip']
    
    def assure_test(self, testname):
        self.send_msg("CHECKTEST", {"name" :testname})
        test_info = self.wait_msg_type("TESTINFO")
        assert test_info.params["name"] == testname
        if not (test_info.params["installed"] and test_info.params["supported"]):
            raise ProtocolError("Test {0} is not supported on the other side".format(test_info.error))
        
    
class NSTSConnectionClient(NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionClient, self).__init__(connection)
    
    def run_test(self, test):
        """
        Execute a complete test on get results back
        """
        
        logger.info("Starting test '{0}'".format(test.friendly_name))
        
        logger.debug("Checking test '{0}'".format(test.name))
        self.assure_test(test.name)
        
        # PREPARE
        logger.debug("Preparing test '{0}'".format(test.name))
        test.initialize(self.local_ip, self.remote_ip)
        self.send_msg("PREPARETEST", {"name":test.name})
        self.wait_msg_type("OK")
        test.prepare_client()
        
        # START
        logger.debug("Starting test '{0}'".format(test.name))
        self.send_msg("STARTTEST", {"name", test.name})
        self.wait_msg_type("OK")
        test.start_client()
        
        logger.debug("Waiting test {0} to finish".format(test.name))
        while test.is_running():
            print "waiting"
            time.sleep(0.2)
            
        # STOP
        logger.debug("Test '{0}' finished.".format(test.name))
        self.send_msg("STOPTEST", {"name", test.name})
        self.wait_msg_type("OK")
        test.stop_client()
        
        # COLLECT
        logger.debug("Collect test '{0}' output".format(test.name))
        self.send_msg("COLLECTOUTPUT", {"name", test.name})
        output_msg = self.wait_msg_type("OUTPUT")
        test.push_output(output_msg.params['output'])
        
        return test.get_results()

class NSTSConnectionServer(NSTSConnectionBase):
    
    def __init__(self, connection):
        super(NSTSConnectionServer, self).__init__(connection)
    
    def checktest(self, tests, name):
        installed = tests.has_key(name)
        supported = False
        if installed:
            supported = tests[name].is_supported()
        self.send_msg("TESTINFO",{
                    "name" : name,
                    "installed" : installed,
                    "supported" : supported,
                    })

    def run_test(self, test):
        logger.info("Client request for executing test {0}.".format(test.friendly_name))
        
        # PREPARE
        test.initialize(self.local_ip, self.remote_ip)
        logger.debug("Preparing test '{0}'.".format(test.name))
        test.prepare_server()
        self.send_msg("OK")
        
        # START
        logger.debug("Starting test '{0}'.".format(test.name))
        self.wait_msg_type("STARTTEST")
        test.start_server()
        self.send_msg("OK")
        
        logger.debug("Waiting test '{0}' to finish.".format(test.name))
        while test.is_running():
            print "waiting"
            time.sleep(0.2)
            
        # STOP
        logger.debug("Test '{0}' finished.".format(test.name))
        self.wait_msg_type("STOPTEST")
        test.stop_server()
        self.send_msg("OK")
        
        # OUTPUT
        logger.debug("Waiting for collection output of test '{0}'.".format(test.name))
        self.wait_msg_type("COLLECTOUTPUT")
        self.send_msg("OUTPUT", {"name": test.name, "output" :test.get_output()})
        
    def process_client_requets(self, tests):
        
        while(True):
            msg = self.wait_msg()
            
            if msg.type_ == "CHECKTEST":
                self.checktest(tests, msg.params["name"])
            elif msg.type_ == "PREPARETEST":
                self.run_test(tests[msg.params['name']])

class Server(object):
    
    def __init__(self, host = None , port = None):
        self.host = '' if host is None else host
        self.port = 26532 if port is None else port
        self.tests = test.get_enabled_tests()

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
        # Get new connections loop
        while(True):
            print "Waiting for new connection..."
            (socket_conn, socket_addr) = self.server_socket.accept()
            print 'Server: got connection from client ' + socket_addr[0] + ':' + str(socket_addr[1])
            try:
                connection = NSTSConnectionServer(socket_conn)
                connection.handshake(socket_addr[0])
                connection.process_client_requets(self.tests)
            except (ConnectionClosedException, socket.error), msg:
                print "Client disconnected."
                
class Client(object):
    
    def __init__(self, remote_host , remote_port = None):
        self.remote_host = remote_host
        self.remote_port = 26532 if remote_port is None else remote_port
        self.connection = None
        self.tests = test.get_enabled_tests()
        
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
        
            
    def run_test(self, test_name):
        return self.connection.run_test(self.tests[test_name])
        