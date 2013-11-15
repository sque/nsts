'''
Created on Nov 3, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import os, math
try:
    import numpy as np
except ImportError:
    pass

def which(program):
    '''
    @ref http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    '''
    import os
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, _ = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def check_pid(pid):
    """
    Check For the existence of a unix pid.
    """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

class InHouseUnitsStatisticsArray(object):
    '''
    Implementation of UnitsStatisticsArray using in house routines
    '''
    def __calc_mean(self, array):
        '''
        A basic function to calculate mean
        '''
        
        values_sum = float(sum(array, float(0)))
        return values_sum/float(len(array))
    
    
    def __init__(self, array):
        self.unit_type = type(array[0])
        self.raw_array = [a.raw_value for a in array]
        self.__raw_mean = self.__calc_mean(self.raw_array)
        self.__raw_min = float(min(self.raw_array))
        self.__raw_max = float(max(self.raw_array))
        # Root( Sum( Square(difference with mean))) 
        self.__raw_std = math.sqrt(
                    self.__calc_mean(
                        [(a - self.__raw_mean)**2 for a in self.raw_array]))

    def max(self):
        return self.unit_type(self.__raw_max)
    
    def min(self):
        return self.unit_type(self.__raw_min)
    
    def mean(self):
        return self.unit_type(self.__raw_mean)
    
    def std(self):
        return self.unit_type(self.__raw_std)


if np is not None:
    class NumPyUnitsStatisticsArray(object):
        '''
        Implementation of UnitsStatisticsArray using numpy
        '''
        
        def __init__(self, array):
            self.unit_type = type(array[0])
            self.array = np.array([a.raw_value for a in array])
            
        def max(self):
            return self.unit_type(self.array.max())
        
        def min(self):
            return self.unit_type(self.array.min())
        
        def mean(self):
            return self.unit_type(self.array.mean())
        
        def std(self):
            return self.unit_type(self.array.std())
    UnitsStatisticsArray = NumPyUnitsStatisticsArray
else:
    UnitsStatisticsArray = InHouseUnitsStatisticsArray
