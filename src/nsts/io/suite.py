'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from nsts.speedtest import SpeedTestSuite, SpeedTest
from nsts.profiles import registry 
from nsts.profiles.base import ExecutionDirection

def parse_command_line(tests):
    '''
    Parse SpeedTestSuite from brief command line
    '''
    suite = SpeedTestSuite()
    
    parsed_profiles = []
    for test in tests.split(","):
        if not "-" in test:
            parsed_profiles.append([test, ExecutionDirection("send")])
            parsed_profiles.append([test, ExecutionDirection("receive")])
            
        else:
            parts = test.split("-")
            profile_id = test[0]
            direction = ExecutionDirection(parts[1]) 
            parsed_profiles.append([profile_id, direction])
            
    for p in parsed_profiles:
        if not registry.is_registered(p[0]):
            raise LookupError("There is no profile with name '{0}'".format(p[0]))
        profile = registry.get_profile(p[0])
        suite.add_test(SpeedTest(profile, p[1]))
    return suite