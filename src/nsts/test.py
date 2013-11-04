'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import subprocess as proc, logging, random
import utils, proto

# Module logger
logger = logging.getLogger("test")

class TestExecutor(object):
    '''
    Base class for implementing a peer executor
    '''
    
    def __init__(self, owner):
        assert isinstance(owner, Test)
        self.owner = owner
        self.connection = None
        self.logger = logging.getLogger("test.{0}".format(self.owner.name))
        
    def initialize(self, connection):
        '''
        Called by the nsts system to initialize executor
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
    
    def is_supported(self):
        raise NotImplementedError()
    
    def prepare(self):
        raise NotImplementedError()
    
    def run(self):
        raise NotImplementedError()
    
    def get_results(self):
        raise NotImplementedError()

class Test(object):
    '''
    Base class for implementing a test
    '''
    def __init__(self, name, friendly_name, client_executor, server_executor):
        self.name = name
        self.friendly_name = friendly_name
        
        assert issubclass(client_executor, TestExecutor)
        assert issubclass(server_executor, TestExecutor)
        self.client_executor = client_executor(self)
        self.server_executor = server_executor(self)

    def initialize(self, local_ip, remote_ip):
        pass

class DummyTestServer(TestExecutor):
    
    def __init__(self, owner):
        super(DummyTestServer, self).__init__(owner)
        
    def prepare(self):
        return True
    
    def run(self):
        self.results = random.random()
        self.logger.debug("Results are generated. sending them to client.")
        self.send_msg("RESULTS", {"results" : self.results})
    
    def get_results(self):
        return self.results

class DummyTestClient(TestExecutor):
    
    def __init__(self, owner):
        super(DummyTestClient, self).__init__(owner)
        
    def prepare(self):
        return True
    
    def run(self):
        msg_results = self.wait_msg_type("RESULTS")
        self.results = msg_results.params['results']
    
    def get_results(self):
        return self.results

class DummyTest(Test):
    def __init__(self):
        super(DummyTest, self).__init__("dummy", "Dummy Test", DummyTestClient, DummyTestServer)
        
    def is_supported(self):
        return True

class IperfTestBase(Test):

    def __init__(self, name, friendly_name):
        super(IperfTestBase, self).__init__(name, friendly_name)
        self.iperf_executable = utils.which('iperf')
        self.iperf_process = None
    
    def execute_iperf(self, extra_args):
        args = [self.iperf_executable]
        args.extend(extra_args)
        logger.debug("Executing iperf - {0}.".format(args))
        self.iperf_process = proc.Popen(args, stdout = proc.PIPE)
    
    def is_iperf_running(self):
        if self.iperf_process is None:
            return False
        
        self.iperf_process.poll()
        return self.iperf_process.returncode is None
    
    def kill_iperf(self):
        logger.debug("Request to kill iperf")
        if not self.is_iperf_running():
            return False
        
        self.iperf_process.kill()
        self.iperf_process = None
        
    def get_iperf_output(self):
        if self.iperf_process is None:
            return False
        
        print "getting output"
        (output, _) = self.iperf_executable.communicate()
        return output
        
class IperfTCPSend(IperfTestBase):
    
    def __init__(self):
        super(IperfTCPSend, self).__init__("iperf", "TCP send (iperf)")
    
    def is_supported(self):
        return self.iperf_executable is not None
    
    def prepare_server(self):
        self.execute_iperf(["-s"])
    
    def prepare_client(self):
        return True
    
    def start_server(self):
        return True
    
    def start_client(self):
        self.execute_iperf(["-t", "1", "-c", self.remote_ip])
    
    def stop_server(self):
        self.kill_iperf()
    
    def stop_client(self):
        print "FINISHED ", type(self.get_iperf_output())
    
    def is_running(self):
        return self.is_iperf_running()
    
    def get_output(self):
        return ""
    
    def push_output(self, output):
        self.results = 123
    
    def get_results(self):
        return self.results
    
# A list with all enabled tests
__enabled_tests = [DummyTest]


def get_enabled_tests():
    '''
    Get a dictionary with instances of all enabled
    tests
    '''
    tests = {}
    for test_class in __enabled_tests:
        test = test_class()
        tests[test.name] = test
        
    return tests