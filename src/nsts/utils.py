'''
Created on Nov 3, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import numpy as np

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


class StatisticsArray(object):
    
    def __init__(self, array):
        self.array = np.array(array)
        
    def max(self):
        return self.array.max()
    
    def min(self):
        return self.array.min()
    
    def mean(self):
        return self.array.mean()
    
    def std(self):
        return self.array.std()