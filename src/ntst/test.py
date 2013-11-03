'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import subprocess as proc, logging
import utils

# Module logger
logger = logging.getLogger("test")

class NetTest(object):
    
    def __init__(self, name, friendly_name):
        self.name = name
        self.friendly_name = friendly_name
        self.options = {}
        
    def initialize(self, local_ip, remote_ip):
        self.local_ip = local_ip
        self.remote_ip = remote_ip

    def is_supported(self):
        raise NotImplementedError("Test.is_supported")
    
    def prepare_server(self):
        raise NotImplementedError("Test.prepare_server")
    
    def prepare_client(self):
        raise NotImplementedError("Test.prepare_client")
    
    def start_server(self):
        raise NotImplementedError("Test.start_server")
    
    def start_client(self):
        raise NotImplementedError("Test.start_client")
    
    def stop_server(self):
        raise NotImplementedError("Test.stop_server")
    
    def stop_client(self):
        raise NotImplementedError("Test.stop_client")
    
    def is_running(self):
        raise NotImplementedError("Test.start_client")
    
    def get_output(self):
        raise NotImplementedError("Test.get_output")
    
    def push_output(self, output):
        raise NotImplementedError("Test.push_output")
    
    def get_results(self):
        raise NotImplementedError("Test.get_results")

class DummyTest(NetTest):
    def __init__(self):
        super(DummyTest, self).__init__("dummy", "Dummy Test ")
        
    def is_supported(self):
        return True
    
    def prepare_server(self):
        return True
    
    def prepare_client(self):
        return True
    
    def start_server(self):
        return True
    
    def start_client(self):
        return True
    
    def stop_server(self):
        return True
    
    def stop_client(self):
        return True
    
    def is_running(self):
        return False
    
    def get_output(self):
        return "DummyDummy --RES--123--RES DUMMY"
    
    def push_output(self, output):
        self.results = 123
    
    def get_results(self):
        return self.results

class IperfTestBase(NetTest):

    def __init__(self, name, friendly_name):
        super(IperfTestBase, self).__init__(name, friendly_name)
        self.iperf_executable = utils.which('iperf')
        self.iperf_process = None
    
    def execute_iperf(self, extra_args):
        args = [self.iperf_executable]
        logger.debug("Executing iperf - {0}.".format(args))
        args.extend(extra_args)
        self.iperf_process = proc.Popen(args)
    
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
        self.execute_iperf(["-c", self.remote_ip])
    
    def stop_server(self):
        self.kill_iperf()
    
    def stop_client(self):
        return True
    
    def is_running(self):
        return self.is_iperf_running()
    
    def get_output(self):
        return ""
    
    def push_output(self, output):
        self.results = 123
    
    def get_results(self):
        return self.results
    
# A list with all enabled tests
__enabled_tests = [IperfTCPSend, DummyTest]


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