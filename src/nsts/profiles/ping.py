'''
Created on Nov 6, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''
import time
from nsts.profiles.base import SpeedTestRuntimeError, ProfileExecutor, Profile
from nsts import units
from subprocess import SubProcessExecutorBase


class PingExecutorSender(SubProcessExecutorBase):

    def __init__(self, context):
        executable = 'ping'
        if context.connection.is_ipv6():
            executable = 'ping6'
        super(PingExecutorSender, self).__init__(context, executable)

    def prepare(self):
        pass

    def parse_and_store_output(self):
        output = self.get_subprocess_output()

        lines = output.split("\n")
        try:
            if lines[-2][:3] != 'rtt':
                raise LookupError(lines)
        except LookupError:
            self.logger.error("ping failed to complete." + str(output))
            raise SpeedTestRuntimeError(
                "Ping failed to complete: " + str(output))

        values = lines[-2].split()[3].split("/")
        unit_name = lines[-2].split()[4]
        rtt = units.Time(values[0] + " " + unit_name)
        self.store_result('rtt', rtt)

    def run(self):
        self.execute_subprocess("-c", "1", self.context.connection.remote_addr)

        while self.is_subprocess_running():
            time.sleep(0.2)

        self.logger.debug("ping stopped running.")

        # Parse output
        self.parse_and_store_output()
        self.propagate_results()


class PingExecutorReceiver(ProfileExecutor):

    def __init__(self, owner):
        super(PingExecutorReceiver, self).__init__(owner)

    def run(self):
        self.collect_results()

    def prepare(self):
        return True

    def is_supported(self):
        return True

    def cleanup(self):
        return True

p = Profile(
    "ping", "Ping", PingExecutorSender, PingExecutorReceiver,
    description='A wrapper for "ping" system tool to" +\
        " measure round trip latency')
p.add_result("rtt", "RTT", units.Time)
