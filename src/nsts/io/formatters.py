'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from nsts import core
from nsts.speedtests.base import SpeedTestMultiSampleResults
from grid import  Grid

class BasicFormatter(object):
    
    def __init__(self, width = 80):
        self.width = 80
        self.tests_samples = {}
        print "Network SpeedTest Suite v{version[0]}.{version[1]}.{version[2]}".format(version = core.VERSION)
        print "===================================="
        
    
    def push_test_results(self, test_samples):
        assert isinstance(test_samples, SpeedTestMultiSampleResults)
        
        self.tests_samples[test_samples.test.name] = test_samples
            
        # Show table of analytic results
        print ""
        print test_samples.test.friendly_name
        print "samples: {0} | took: {1} | started: {2}".format(
                len(test_samples.samples),
                test_samples.execution_time().optimal_combined_scale_str(),
                test_samples.started_at)
        grid = Grid(self.width)
        grid.add_column('', width='fit')
        grid.add_column('Took', width='fit')
        for result_entry in test_samples.test.result_descriptors.values():
            grid.add_column(result_entry.friendly_name)
            
        # Push data
        for i, sample in enumerate(test_samples):
            row =[i, sample.execution_time()]
            row.extend(sample.values.values())
            
            grid.add_row(row)
        print grid
    def finish(self):
        
        print ""
        print "{0:=<{width}}".format("", width = self.width)
        print " Overall Statistics"
        print "{0:=<{width}}".format("", width = self.width)
        
        
        for samples in self.tests_samples.values():
            print ""
            print samples.test.friendly_name
            grid = Grid(self.width)
            grid.add_column('', width='fit')
            grid.add_column('Metric', width='fit')
            grid.add_column('Mean', width='equal')
            grid.add_column('Min', width='equal')
            grid.add_column('Max', width='equal')
            grid.add_column('StdDev', width='equal')
        
            statistics = samples.get_statistics()
            for i, metric_name in enumerate(statistics):
                metric_stats = statistics[metric_name]
                grid.add_row([
                    i,
                    samples.test.result_descriptors[metric_name].friendly_name,
                    metric_stats['mean'],
                    metric_stats['min'],
                    metric_stats['max'],
                    metric_stats['std']])
            print grid