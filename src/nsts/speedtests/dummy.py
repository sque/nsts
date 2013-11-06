'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import random
import base
from nsts import units


class DummyTestServer(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(DummyTestServer, self).__init__(owner)
        
    def is_supported(self):
        return True
    
    def prepare(self):
        return True
    
    def run(self):
        self.store_result('random_transfer', units.BitRateUnit(random.random()))
        self.store_result('random_time', units.TimeUnit(random.random()))
        self.logger.debug("Results are generated. sending them to client.")
        self.propagate_results()

    def cleanup(self):
        pass
    
class DummyTestClient(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(DummyTestClient, self).__init__(owner)
        
    def is_supported(self):
        return True
    
    def prepare(self):
        return True
    
    def run(self):
        self.collect_results()

    def cleanup(self):
        return True
    
class DummyTest(base.SpeedTest):
    def __init__(self):
        descriptors = [
            base.ResultEntryDescriptor('random_transfer', 'Random Transfer', units.BitRateUnit),
            base.ResultEntryDescriptor('random_time', 'Random Time', units.TimeUnit)
            ]
        super(DummyTest, self).__init__("dummy", "Dummy SpeedTest", DummyTestClient, DummyTestServer, descriptors)

    

base.enable_test(DummyTest)