'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from nsts.speedtests.base import SpeedTestResults
from nsts import core
import numpy as np

def reduce_results(result_set):

    reduced_results = {}
    for test_name, test_results in result_set.iteritems():
        data = np.array([f.results for f in test_results], dtype="float")
        reduced_results[test_name] = (data.mean(), data.std())
    return reduced_results

def basic_formating(result_set):
    assert isinstance(result_set, dict)
    
    # Brief output
    reduced_results = reduce_results(result_set)
    for test_name, res in reduced_results.iteritems():
        print "{0}".format(test_name)
        print "-------------------------------------"
        print "{0} |  {1}({2}) ".format(0, res[0], res[1])
        
    for test_name, results in result_set.iteritems():
        
        print "{0}".format(test_name)
        print "-------------------------------------"
        for i,result in enumerate(results):
            assert isinstance(result, SpeedTestResults)
            print "{0} |  {1} {2} {3}".format(i + 1, result.started_at, result.get_total_seconds(), result.results)
    
    