'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import  pickle, base64, logging

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
        '''
        Request other side to assure that a test is available
        '''
        self.send_msg("CHECKTEST", {"name" :testname})
        test_info = self.wait_msg_type("TESTINFO")
        assert test_info.params["name"] == testname
        if not (test_info.params["installed"] and test_info.params["supported"]):
            raise ProtocolError("Test {0} is not supported on the other side".format(test_info.error))

