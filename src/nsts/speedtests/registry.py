'''
Created on Nov 12, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from base import SpeedTestDescriptor
from collections import OrderedDict

# The list with all registered speedtests
__registered_speedtests = OrderedDict()

def is_registered(test_id):
    '''
    Check if test is registered by its id
    '''
    tests = get_all()
    
    return test_id in [t.id for t in tests]

def register(descriptor):
    '''
    Register a test in registry
    '''
    global __registered_speedtests
    
    assert isinstance(descriptor, SpeedTestDescriptor)
    if not is_registered(descriptor.id):
        __registered_speedtests[descriptor.id] = descriptor

def get_all():
    '''
    Get a list with all registered tests
    '''
    return __registered_speedtests.values()


def get_test(test_id):
    '''
    Get access to a specific test descriptor
    '''
    return __registered_speedtests[test_id]

