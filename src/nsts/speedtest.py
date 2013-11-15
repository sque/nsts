'''
Created on Nov 13, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from nsts.profiles.base import Profile, ProfileExecution, \
    ExecutionDirection

from nsts import utils
from units import TimeUnit
from nsts.options import OptionsDescriptor, Options

"""
class SpeedTestOptions(object):
    
    def __init__(self, profile, values = {}):
        self.__profile = profile
        self.__supported_options = []
        for opt in profile.supported_options:
            self.__supported_options[profile.id + "." + opt.id] = profile.supported_options[opt]
        self.__supported_options.append(
            OptionValueDescriptor('interval', '',TimeUnit, 0))
        self.__supported_options.append(
            OptionValueDescriptor('samples', '',int,5))
        
        self.load_values(values)    # Load default values
    
    @property
    def profile(self):
        return self.__profile
    
    @property
    def profile_options(self):
        return self.__profile_options
    
    @property
    def test_options(self):
        return self.__test_options
    
    def __is_profile_option_id(self, optid):
        if optid[:len(self.profile.id)+1] == self.profile.id + '.':
            return True

    def __strip_profile_id(self, optid):
        return optid[len(self.profile.id)+1:]

    def load_values(self, options):
        self.__test_options = {}
        self.__profile_options = {}
        
        # Load default values
        for opt in self.__supported_options:
            if opt.default is None:
                continue
            if self.__is_profile_option_id(opt.id):
                prof_optid = self.__strip_profile_id(opt.id)
                self.__profile_options[prof_optid] = opt.default
            else:
                self.__test_options[opt.id] = opt.default
        
        # Load user-defined values
        for opt in options:
            if not self.__supported_options.has_key(opt.id):
                raise OptionError("Test does not support option {1}".format(opt.id))
            opt_desc = self.__supported_options[opt.id]

            if self.__is_profile_option_id(opt.id):
                prof_optid = self.__strip_profile_id(opt.id)
                self.__profile_options[prof_optid] = opt_desc.type(options[opt.id])
            else:
                self.__test_options[opt.id] = opt_desc.type(options[opt.id])  
"""

class SpeedTestOptionsDescriptor(OptionsDescriptor):
    
    def __init__(self):
        super(SpeedTestOptionsDescriptor, self).__init__()
        self.add_option('interval', '',TimeUnit)
        self.add_option('samples', '',int)

class SpeedTest(object):
    '''
    A SpeedTest involves running a profile with specific
    options and gathering results.
    '''
    def __init__(self, profile, direction, options = {}):
        assert isinstance(profile, Profile)
        assert isinstance(direction, ExecutionDirection)

        self.__profile = profile
        self.__direction = direction
        self.__options = Options(SpeedTestOptionsDescriptor())
        self.__profile_options = Options(profile.supported_options)
        self.samples = []

    @property
    def profile(self):
        '''
        Get profile object that was used for this execution
        '''
        return self.__profile
    
    @property
    def name(self):
        '''
        Get Test name
        '''
        return "{0} ({1})".format(self.profile.name, self.direction)
    
    @property
    def options(self):
        '''
        Get SpeedTestOptions object that hold all option values
        '''
        return self.__options
    
    @property
    def profile_options(self):
        '''
        Get profile options object
        '''
        return self.__profile_options
    
    @property
    def direction(self):
        '''
        Get direction that test was executed
        '''
        return self.__direction
    
    @property
    def started_at(self):
        '''
        Get when was the first sample executed.
        '''
        return self.samples[0].started_at
    
    def push_sample(self, sample):
        '''
        Push another sample in the execution list
        '''
        assert isinstance(sample, ProfileExecution)
        self.samples.append(sample)
    
    def statistics(self):
        '''
        Calculate statistics on samples
        '''
        reduced = {}
        for result_entry in self.profile.supported_results.values():
            
            # Collect all samples raw values
            data = utils.UnitsStatisticsArray([sample.results[result_entry.id] for sample in self.samples])
            
            reduced_entry = {
                'mean' :  data.mean(),
                'min' :  data.min(),
                'max' :  data.max(),
                'std' :  data.std(),
            }
            
            reduced[result_entry.id] = reduced_entry

        return reduced
    
    def execution_time(self):
        '''
        Get total execution time for all samples
        '''
        return sum([s.execution_time() for s in self.samples], TimeUnit(0))
    
    def __iter__(self):
        return self.samples.__iter__()


class SpeedTestSuite(object):
    
    def __init__(self):
        self.tests = []
        self.__options = Options(SpeedTestOptionsDescriptor())
        
    @property
    def options(self):
        return self.__options
        
    def add_test(self, test):
        assert isinstance(test, SpeedTest)
        self.tests.append(test)
        
