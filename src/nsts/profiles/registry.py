'''
Created on Nov 12, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

from base import Profile
from collections import OrderedDict

# The list with all registered profiles
__registered_profiles = OrderedDict()

def is_registered(test_id):
    '''
    Check if test is registered by its id
    '''
    tests = get_all()
    
    return test_id in [t.id for t in tests]

def register(profile):
    '''
    Register a profile in registry
    '''
    global __registered_profiles
    
    assert isinstance(profile, Profile)
    if not is_registered(profile.id):
        __registered_profiles[profile.id] = profile

def get_all():
    '''
    Get a list with all registered profiles
    '''
    return __registered_profiles.values()


def get_profile(prof_id):
    '''
    Get access to a specific profile
    @raise LookupError on failure
    '''
    if not is_registered(prof_id):
        raise LookupError("There is no profile with name '{0}'".format(prof_id))
    return __registered_profiles[prof_id]

