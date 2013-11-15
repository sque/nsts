'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import datetime, sys
from nsts import core
from nsts.speedtest import SpeedTest, SpeedTestSuite
from nsts.options import OptionsDescriptor, Options
from grid import  Grid
from nsts.profiles.base import ProfileExecution

class ClientTerminalOptionsDescriptor(OptionsDescriptor):
    
    def __init__(self):
        super(ClientTerminalOptionsDescriptor, self).__init__()
        self.add_option('host', 'Host that client connected at', unicode)
        self.add_option('port', 'Port that client connected at', int)
        self.add_option('suite', 'Suite that is executed', unicode)
        self.add_option('samples', 'Default samples', int)
        self.add_option('interval', 'Default interval', int)
        self.add_option('verbose', 'Verbose level', bool, False)

class ClientTerminal(object):
    '''
    Base class for interacting with client terminal
    '''
    
    def __init__(self):
        self.__supported_options = ClientTerminalOptionsDescriptor()
        self.__options = Options(self.__supported_options)

    @property
    def options(self):
        '''
        Access options values of ClientTerminal
        '''
        return self.__options

    def welcome(self):
        '''
        It is the first message to be printed
        '''
        pass
    
    def client_connected(self):
        '''
        Called when client managed to connect
        '''
        pass
    
    def profile_execution_started(self, profile):
        '''
        Called when profile has started execution
        '''
        pass
    
    def profile_execution_finished(self, profile):
        '''
        Called when profile has finished
        '''
        pass
    
    def test_execution_started(self, test):
        '''
        Called when a test execution has started
        '''
        pass
    
    def test_execution_finished(self, test):
        '''
        Called when a test execution has finished
        '''
        pass
    
    def suite_execution_started(self, suite):
        '''
        Called when suite execution has started
        '''
        pass
    
    def suite_execution_finished(self, suite):
        '''
        Called when suite execution has finished
        '''
        pass
    
    def epilog(self):
        '''
        Called at the end of program execution
        '''
        pass

class BasicTerminal(ClientTerminal):
    '''
    The basic terminal is the default terminal that is
    expected to read by humans
    '''
    
    def __init__(self):
        super(BasicTerminal, self).__init__()
        self.width = 80

    def __print_test_properties(self, test):
        print "samples: {0} | took: {1} | started: {2}".format(
                len(test.samples),
                test.execution_time().optimal_combined_scale_str(),
                test.started_at)
        
    def welcome(self):
        print "Network SpeedTest Suite [NSTS] Version {version[0]}.{version[1]}.{version[2]}".format(version = core.VERSION)
        print "Free-software published under GPLv3 license."
        print "http://github.com/sque/nsts"
        print ""
        
    def client_connected(self):
        print "Started at:", datetime.datetime.now()
        print "Server    : {0}:{1}".format(self.options['host'], self.options['port'])
        print "{0:-<{width}}".format("",width = self.width)
        #print " MultiSampling: {0}".format(self.options['samples'])
    
    def profile_execution_finished(self, profile):
        assert isinstance(profile, ProfileExecution)
        if not self.options['verbose']:
            sys.stdout.write('.')
            sys.stdout.flush()
    
    def test_execution_started(self, test):
        if self.options['verbose']:
            print '\n{0}: '.format(test.name)
        else:
            print '{0}: '.format(test.name),
        
    def test_execution_finished(self, test):
        assert isinstance(test, SpeedTest)
        if not self.options['verbose']:
            print '{0} samples, Done!'.format(len(test.samples))
        else:
            self.__print_test_properties(test)
            grid = Grid(self.width)
            grid.add_column('', width='fit')
            grid.add_column('Took', width='fit')
            for result_entry in test.profile.supported_results.values():
                grid.add_column(result_entry.name)
            # Push data
            for i, sample in enumerate(test):
                row =[i+1, sample.execution_time()]
                row.extend(sample.results.values())
                
                grid.add_row(row)
            print grid
    
    def suite_execution_finished(self, suite):
        assert isinstance(suite, SpeedTestSuite)
        
        print ""
        print "{0:=<{width}}".format("", width = self.width)
        print " SpeedTest Suite statistics"
        print "{0:=<{width}}".format("", width = self.width)
        
        for test in suite.tests:
            print ""
            print test.name
            print "samples: {0} | took: {1} | started: {2}".format(
                len(test.samples),
                test.execution_time().optimal_combined_scale_str(),
                test.started_at)
            grid = Grid(self.width)
            grid.add_column('Metric', width='fit')
            grid.add_column('Mean', width='equal')
            grid.add_column('Min', width='equal')
            grid.add_column('Max', width='equal')
            grid.add_column('StdDev', width='equal')
        
            statistics = test.statistics()
            for _, metric_name in enumerate(statistics):
                metric_stats = statistics[metric_name]
                grid.add_row([
                    test.profile.supported_results[metric_name].name,
                    metric_stats['mean'],
                    metric_stats['min'],
                    metric_stats['max'],
                    metric_stats['std']])
            print grid
    
    def epilog(self):
        print 'Bye!'
