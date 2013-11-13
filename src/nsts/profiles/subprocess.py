'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
from __future__ import absolute_import
from .base import SpeedTestExecutor
from nsts import utils
import subprocess as proc

class SubProcessExecutorBase(SpeedTestExecutor):

    def __init__(self, owner, binary_name):
        super(SubProcessExecutorBase, self).__init__(owner)
        self.subprocess_executable = utils.which(binary_name)
        self.subprocess_handle = None
    
    def execute_subprocess(self, *extra_args):
        args = [self.subprocess_executable]
        args.extend(extra_args)
        self.logger.debug("Starting subprocess - {0}.".format(args))
        self.subprocess_handle = proc.Popen(args, stdout = proc.PIPE, stderr = proc.STDOUT, close_fds=True)
        
    def is_supported(self):
        return self.subprocess_executable is not None
    
    def is_subprocess_running(self):
        if self.subprocess_handle is None:
            return False
        
        self.subprocess_handle.poll()
        return self.subprocess_handle.returncode is None
    
    def kill_subprocess(self):
        self.logger.debug("Request to kill subprocess")
        if not self.is_subprocess_running():
            return False
        
        self.subprocess_handle.kill()
        self.subprocess_handle = None
        
    def get_subprocess_output(self):
        if self.subprocess_handle is None:
            return False

        (output, _) = self.subprocess_handle.communicate()
        return output

    def cleanup(self):
        self.kill_subprocess()
