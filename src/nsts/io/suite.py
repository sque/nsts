'''
Created on Nov 2, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from nsts.speedtest import SpeedTestSuite, SpeedTest
from nsts.profiles import registry 
from nsts.profiles.base import ExecutionDirection
import ConfigParser

class ParseError(IOError):
    pass

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
        profile = registry.get_profile(p[0])
        suite.add_test(SpeedTest(profile, p[1]))
    return suite


def load_file(suite_filename):
    '''
    Parse a suite filename and return the SpeedTestSuite object
    '''
    suite = SpeedTestSuite()
    
    config = ConfigParser.ConfigParser()
    config.read(suite_filename)
    
    # Read global options
    if 'global' in config.sections():
        for opt in config.options('global'):
            suite.options[opt] = config.get('global', opt)
        config.remove_section('global')
    
    for test_id in config.sections():
        if 'profile' not in config.options(test_id):
            raise ParseError("'profile' entry is mandatory for every test")
        if 'direction' in config.options(test_id):
            direction = [ExecutionDirection(config.get(test_id, 'direction'))]
            config.remove_option(test_id, 'direction')
        else:
            direction = [ExecutionDirection('s'), ExecutionDirection('r')]
        
        prof_id = config.get(test_id, 'profile')
        profile = registry.get_profile(prof_id)
        config.remove_option(test_id, 'profile')

        
        # Load options only for profiles
        profile_options = {}
        for opt in config.options(test_id):
            if opt[:len(prof_id)] == prof_id:
                profile_options[opt[len(prof_id)+1:]] = config.get(test_id, opt)
                config.remove_option(test_id, opt)
        
        # The rest are for test itself
        for direct in direction:
            test = SpeedTest(profile, direct, profile_options)
            for opt in config.options(test_id):
                test.options[opt] = config.get(test_id, opt)
            suite.add_test(test)
            
    
    return suite
