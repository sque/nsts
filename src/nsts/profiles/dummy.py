'''
Created on Nov 4, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import random
from base import ProfileExecutor, Profile
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
        self.store_result(
            'random_transfer',
            units.BitRate(random.uniform(min_trans, max_trans)))
        self.store_result(
            'random_time',
            units.Time(random.uniform(min_time, max_time)))
        self.logger.debug(
            "Results have been generated. Sending them to client...")
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

p = Profile(
    "dummy", "Dummy SpeedTest", DummyTestSender, DummyTestReceiver,
    "A truly dummy test that returns some random numbers.")
p.supported_options.add_option(
    'min_transfer', 'The minimum random value of transfer',
    units.BitRate, default=0)
p.supported_options.add_option(
    'max_transfer', 'The maximum random value of transfer',
    units.BitRate, default=1)
p.supported_options.add_option(
    'min_time', 'The minimum random value of time',
    units.Time, default=0)
p.supported_options.add_option(
    'max_time', 'The maximum random value of time',
    units.Time, default=1)
p.add_result('random_transfer', 'Random Transfer', units.BitRate)
p.add_result('random_time', 'Random Time', units.Time)
