'''
Created on Nov 13, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''
from nsts.profiles.base import Profile, ProfileExecution, \
    ExecutionDirection

from nsts import utils
from units import Time
from nsts.options import OptionsDescriptor, Options


class SpeedTestOptionsDescriptor(OptionsDescriptor):

    def __init__(self):
        super(SpeedTestOptionsDescriptor, self).__init__()
        self.add_option('interval', '', Time)
        self.add_option('samples', '', int)
        self.add_option('name', '', unicode)


class SpeedTest(object):
    '''
    A SpeedTest involves running a profile with specific
    options and gathering results.
    '''
    def __init__(self, profile, direction, profile_options={}):
        assert isinstance(profile, Profile)
        assert isinstance(direction, ExecutionDirection)

        self.__profile = profile
        self.__direction = direction
        self.__options = Options(SpeedTestOptionsDescriptor())
        self.__profile_options = Options(
            profile.supported_options, profile_options)
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
        if self.options['name'] is None:
            return "{0} ({1})".format(self.profile.name, self.direction)
        else:
            return "{0} ({1})".format(self.options['name'], self.direction)

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
            data = utils.UnitsStatisticsArray(
                [sample.results[result_entry.id] for sample in self.samples])

            reduced_entry = {
                'mean':  data.mean(),
                'min':  data.min(),
                'max':  data.max(),
                'std':  data.std()}

            reduced[result_entry.id] = reduced_entry

        return reduced

    def execution_time(self):
        '''
        Get total execution time for all samples
        '''
        return sum([s.execution_time() for s in self.samples], Time(0))

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
