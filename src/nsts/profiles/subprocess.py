'''
Module with helper functionality for executors to spawn
and control child processes.

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''
from __future__ import absolute_import
from .base import ProfileExecutor
from nsts import utils
import subprocess as proc


class SubProcessExecutorBase(ProfileExecutor):
    '''
    Base class for executors that depends on executing an external process
    in order to perform a benchmark.
    '''

    def __init__(self, context, binary_name):
        '''
        @param context The execution context
        @param binary_name The filename of the application binary to be
            spawned.
        @see ProfileExecutor
        '''
        super(SubProcessExecutorBase, self).__init__(context)
        self.subprocess_executable = utils.which(binary_name)
        self.subprocess_handle = None

    def execute_subprocess(self, *args):
        '''
        Execute and control a subprocess of the given application.
        @param args These arguments will be passed directly to subprocess
        '''
        if self.is_subprocess_running():
            raise RuntimeError("Cannot execute multiple "
                               "subprocesses simultaneously.")
        proc_args = [self.subprocess_executable]
        proc_args.extend(args)
        self.logger.debug("Starting subprocess - {0}.".format(proc_args))
        self.subprocess_handle = proc.Popen(args, stdout=proc.PIPE,
                                            stderr=proc.STDOUT, close_fds=True)

    def is_supported(self):
        return self.subprocess_executable is not None

    def is_subprocess_running(self):
        '''
        Check if the subprocess is still running
        '''
        if self.subprocess_handle is None:
            return False

        self.subprocess_handle.poll()
        return self.subprocess_handle.returncode is None

    def kill_subprocess(self):
        '''
        Aggressive kill of the spawned subprocess.
        '''
        self.logger.debug("Request to kill subprocess")
        if not self.is_subprocess_running():
            return False

        self.subprocess_handle.kill()
        self.subprocess_handle = None

    def get_subprocess_output(self):
        '''
        Get all the output of the spawned subprocess
        '''
        if self.subprocess_handle is None:
            return False

        (output, _) = self.subprocess_handle.communicate()
        return output

    def cleanup(self):
        self.kill_subprocess()
