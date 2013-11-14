'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import random
from base import ProfileExecutor, Profile
from registry import register
from nsts import units


class DummyTestSender(ProfileExecutor):
        
    def is_supported(self):
        return True
    
    def prepare(self):
        pass
    
    def run(self):
        self.store_result('random_transfer', units.BitRateUnit(random.random()))
        self.store_result('random_time', units.TimeUnit(random.random()))
        self.logger.debug("Results have been generated. Sending them to client...")
        self.propagate_results()

    def cleanup(self):
        pass
    
class DummyTestReceiver(ProfileExecutor):
    
    def is_supported(self):
        return True
    
    def prepare(self):
        pass
    
    def run(self):
        self.collect_results()

    def cleanup(self):
        pass
    
class DummyTest(Profile):
    def __init__(self):
        super(DummyTest, self).__init__(
                "dummy",
                "Dummy SpeedTest",
                DummyTestSender, DummyTestReceiver)
        
        self.add_result('random_transfer', 'Random Transfer', units.BitRateUnit)
        self.add_result('random_time', 'Random Time', units.TimeUnit)

register(DummyTest())