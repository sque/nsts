'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import  pickle, base64, logging, socket

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
        assert isinstance(params, dict)
        
        self.__type = type_
        self.__params = params
    
    @property
    def type(self):
        '''
        Get the type of this message
        '''
        return self.__type
    
    @property
    def params(self):
        '''
        Get parameters of this message
        '''
        return self.__params
    
    @params.setter
    def params(self, params):
        '''
        Set parameters of this message
        '''
        assert isinstance(params, dict)
        self.__params = params
        return self.__params
    
    def encode(self):
        '''
        Encode this message to a plain text format
        '''
        encoded_params = base64.b64encode(pickle.dumps(self.params))
        return "{0} {1}".format(self.type, encoded_params)
    
    @staticmethod
    def decode(raw_msg):
        msg_parts = raw_msg.split(" ")
        try:
            msg_params = pickle.loads(base64.b64decode(msg_parts[1]))
        except Exception, e:
            raise ProtocolError("Error decoding message parameters." + str(e))
        return Message(msg_parts[0], msg_params)
    
    def __str__(self):
        return "[{0} {1}]".format(self.type, self.params)
     
    def __repr__(self):
        return self.__str__()
    
    
class MessageStream(object):
    '''
    Wrapper for exchanging plain-text messages over
    sockets.
    '''
    
    MSG_DELIMITER = "\n"
    
    def __init__(self, socket_):
        assert isinstance(socket_, socket.socket)
        self.__socket = socket_
        self.receiver_buffer = ''
    
    @property
    def socket(self):
        '''
        Get network socket used for this stream
        '''
        return self.__socket
    
    def __buffer_pop_msg(self):
        '''
        Pop a message from the buffer.
        @return None if no messages exists
        '''
        
        end_msg_pos = self.receiver_buffer.find(MessageStream.MSG_DELIMITER)
        if end_msg_pos == -1:
            return None # No line in buffer
        
        # Extract message
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
            data = self.socket.recv(1024)
            if not data:
                raise ConnectionClosedException()
            self.__buffer_push_data(data)
            msg = self.__buffer_pop_msg()
            if msg is not None:
                logger.debug("Received message {0}".format(msg))
                return msg

    def wait_msg_type(self, expected_type):
        '''
        Expect a message from the connection(blocking)
        @param expected_type The type of the expected message
        @raise ProtocolError if another message arrives
        '''
        logger.debug("Waiting for '{0}' message".format(expected_type))
        msg = self.wait_msg()
        
        if msg.type != expected_type:
            logger.debug("Waiting for '{0}' message, but '{1}' arrived".format(expected_type, msg.type))
            raise ProtocolError("Waiting for '{0}' message, but '{1}' arrived".format(expected_type, msg.type))
        return msg
    
    def send_msg(self, msg_type, msg_params = {}):
        '''
        Send a message to the other end.
        '''
        msg = Message(msg_type, msg_params)
        self.socket.send(msg.encode() + MessageStream.MSG_DELIMITER)
        

class NSTSConnectionBase(MessageStream):
    '''
    Implement NSTS connection base
    '''
    
    def __init__(self, socket):
        super(NSTSConnectionBase, self).__init__(socket)
        self.__remote_addr = None
        self.__local_addr = None
    
    @property
    def remote_addr(self):
        '''
        Get public address of remote host
        '''
        return self.__remote_addr

    @property
    def local_addr(self):
        '''
        Get public address of localhost
        '''
        return self.__local_addr
    
    def handshake(self, remote_addr):
        '''
        Handshake between two peers.
        In this process, they will validate version compatibility
        and will exchange needed information.
        '''
        self.__remote_addr = remote_addr
        self.send_msg('HELLO', {"version" : VERSION, "remote_addr": remote_addr})
        response = self.wait_msg_type('HELLO')
        
        if response.params['version'] != VERSION:
            raise ProtocolError("Incompatible version")
        self.__local_addr = response.params['remote_addr']
    
    def assure_profile(self, profile_id):
        '''
        Request other side to assure that a profilet is available
        '''
        self.send_msg("CHECKTEST", {"profile_id" :profile_id})
        test_info = self.wait_msg_type("TESTINFO")
        assert test_info.params["profile_id"] == profile_id
        if not (test_info.params["installed"] and test_info.params["supported"]):
            raise ProtocolError("Test {0} is not supported on the other side".format(test_info.error))

