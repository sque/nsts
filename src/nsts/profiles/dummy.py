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
        min_trans = self.context.options['min_transfer'].raw_value
        max_trans = self.context.options['max_transfer'].raw_value
        min_time = self.context.options['min_time'].raw_value
        max_time = self.context.options['max_time'].raw_value
        self.store_result('random_transfer',
            units.BitRateUnit(random.uniform(min_trans, max_trans)))
        self.store_result('random_time',
            units.TimeUnit(random.uniform(min_time, max_time)))
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
                DummyTestSender, DummyTestReceiver,
                "A truly dummy test that returns some random numbers.")
        self.supported_options.add_option(
                'min_transfer',
                'The minimum random value of transfer',
                units.BitRateUnit, default =0)
        self.supported_options.add_option(
                'max_transfer',
                'The maximum random value of transfer',
                units.BitRateUnit, default =1)
        self.supported_options.add_option(
                'min_time',
                'The minimum random value of time',
                units.TimeUnit, default =0)
        self.supported_options.add_option(
                'max_time',
                'The maximum random value of time',
                units.TimeUnit, default =1)

        self.add_result('random_transfer', 'Random Transfer', units.BitRateUnit)
        self.add_result('random_time', 'Random Time', units.TimeUnit)
        

register(DummyTest())