'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import time
from nsts.speedtests import base
from nsts import utils, units
from subprocess import SubProcessExecutorBase


class PingExecutorClient(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(PingExecutorClient, self).__init__(owner, 'ping')
        
    def prepare(self):
        return True
    
    def parse_and_store_output(self):
        output = self.get_subprocess_output()
        
        lines = output.split("\n")
        if lines[-2][:3] != 'rtt':
            self.logger.error("ping failed to complete." + str(lines))
            raise base.SpeedTestRuntimeError("Unknown error, ping failed to complete.")
        
        values = lines[-2].split()[3].split("/")
        self.store_result('rtt_min', units.TimeUnit(float(values[0])))
        self.store_result('rtt_avg', units.TimeUnit(float(values[1])))
        self.store_result('rtt_max', units.TimeUnit(float(values[2])))
        self.store_result('rtt_mdev', units.TimeUnit(float(values[3])))
        
    def run(self):
        self.execute_subprocess("-c", "2", self.connection.remote_ip)
        
        while self.is_subprocess_running():
            time.sleep(0.2)
            
        self.logger.debug("ping stopped running.")
        
        # Parse output
        self.parse_and_store_output()
        self.propagate_results()
    

class PingExecutorServer(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(PingExecutorServer, self).__init__(owner)
        
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
                base.ResultEntryDescriptor("rtt_min", "RTT (avg)", units.TimeUnit),
                base.ResultEntryDescriptor("rtt_max", "RTT (max)", units.TimeUnit),
                base.ResultEntryDescriptor("rtt_avg", "RTT (avg)", units.TimeUnit),
                base.ResultEntryDescriptor("rtt_mdev", "RTT (mdev)", units.TimeUnit)
        ]
        super(PingTest, self).__init__("ping", "Ping", PingExecutorClient, PingExecutorServer, descriptors)

base.enable_test(PingTest)
