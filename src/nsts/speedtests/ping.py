'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import time
from nsts.speedtests import base
from nsts import utils, units
from subprocess import SubProcessExecutorBase


class PingExecutorSender(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(PingExecutorSender, self).__init__(owner, 'ping')
        
    def prepare(self):
        return True
    
    def parse_and_store_output(self):
        output = self.get_subprocess_output()
        
        lines = output.split("\n")
        if lines[-2][:3] != 'rtt':
            self.logger.error("ping failed to complete." + str(lines))
            raise base.SpeedTestRuntimeError("Unknown error, ping failed to complete.")
        
        values = lines[-2].split()[3].split("/")
        self.store_result('rtt', units.TimeUnit(float(values[0])))
        
    def run(self):
        self.execute_subprocess("-c", "1", self.connection.remote_addr)
        
        while self.is_subprocess_running():
            time.sleep(0.2)
            
        self.logger.debug("ping stopped running.")
        
        # Parse output
        self.parse_and_store_output()
        self.propagate_results()
    

class PingExecutorReceiver(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(PingExecutorReceiver, self).__init__(owner)
        
    def run(self):
        self.collect_results()
    
    def prepare(self):
        return True
    
    def is_supported(self):
        return True
    
    def cleanup(self):
        return True

class PingTest(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("rtt", "RTT", units.TimeUnit),
        ]
        super(PingTest, self).__init__("ping", "Ping", PingExecutorSender, PingExecutorReceiver, descriptors)

base.enable_test(PingTest)
