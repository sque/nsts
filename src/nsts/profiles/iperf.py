'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import time
from nsts.profiles.base import SpeedTestRuntimeError, ProfileExecutor, Profile
from nsts.profiles import registry
from nsts import units
from subprocess import SubProcessExecutorBase


class IperfExecutorReceiver(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(IperfExecutorReceiver, self).__init__(owner, 'iperf')
        
    def prepare(self):
        return True
    
    def run(self):
        msg = self.wait_msg_type("STARTSERVER")
        self.execute_subprocess(*msg.params['server_arguments'])
        time.sleep(0.2)
        self.send_msg("OK")

        self.wait_msg_type("STOPSERVER")
        self.kill_subprocess()
        self.send_msg("OK")
        
        # Collect __results
        self.collect_results()

class IperfExecutorSender(SubProcessExecutorBase):
    
    def __init__(self, context):
        super(IperfExecutorSender, self).__init__(context, 'iperf')
        self.server_arguments = ["-s"]
        self.client_arguments = [ "-y", "C"]
        if context.connection.is_ipv6():
            self.client_arguments.append('-V')
            self.server_arguments.append('-V')
            
    def prepare(self):
        return True
    
    def parse_and_store_output(self):
        output = self.get_subprocess_output()
        self.store_result('transfer_rate', units.BitRate(float(output.split(',')[8])))
        
    def run(self):
        self.send_msg("STARTSERVER",  {"server_arguments" : self.server_arguments})
        self.wait_msg_type('OK')
        
        self.execute_subprocess(
                "-c", self.context.connection.remote_addr,
                "-t", str(self.context.options['time'].raw_value),
                *self.client_arguments)
        
        while self.is_subprocess_running():
            time.sleep(0.2)
            
        self.logger.debug("iperf stopped running.")
        self.send_msg("STOPSERVER")
        self.wait_msg_type("OK")
        
        # Parse output
        self.parse_and_store_output()
        self.propagate_results()


class IperfJitterExecutorSender(IperfExecutorSender):
    
    def __init__(self, context):
        super(IperfJitterExecutorSender, self).__init__(context)
        self.server_arguments.extend(["-u"])
        self.client_arguments.extend(["-u",
                "-t", str(self.context.options['time'].raw_value),
                "-b", str(self.context.options['rate'].raw_value)])

        
    def parse_and_store_output(self):
        output = self.get_subprocess_output().split("\n")
        
        #sent = output[0].split(',')
        received = output[1].split(',')
        self.store_result('transfer_rate', units.BitRate(received[8]))
        self.store_result('jitter', units.Time(received[9] + "ms"))
        self.store_result('lost_packets', units.Packet(received[10]))
        self.store_result('total_packets', units.Packet(received[11]))
        self.store_result('percentage_lost', units.Percentage(received[12]))
        
class IperfTCPProfile(Profile):
    
    def __init__(self):
        super(IperfTCPProfile, self).__init__(
            "iperf_tcp",
            "TCP (iperf)", IperfExecutorSender, IperfExecutorReceiver,
            'Wrapper for "iperf" benchmark tool, to measure raw TCP throughput.')
        self.add_result("transfer_rate", "Transfer Rate", units.BitRate)
        self.supported_options.add_option(
                'time', 'time to transmit for', units.Time, default=10)
        
class IperfJitterProfile(Profile):
    
    def __init__(self):

        super(IperfJitterProfile, self).__init__(
                "iperf_jitter", "Jitter (iperf)",
                IperfJitterExecutorSender, IperfExecutorReceiver,
                'Wrapper for "iperf" benchmark tool, to measure latency jittering on UDP transmissions')
        self.add_result("transfer_rate", "Trans. Rate", units.BitRate)
        self.add_result("jitter", "Jitter", units.Time)
        self.add_result("lost_packets", "Lost Pck", units.Packet)
        self.add_result("total_packets", "Total Pck", units.Packet)
        self.add_result("percentage_lost", "Lost Pck %", units.Percentage)
        self.supported_options.add_option(
                'time', 'time to transmit for', units.Time, default=10)
        self.supported_options.add_option(
                'rate', 'rate to send udp packages', units.BitRate, default="1 Mbps")

registry.register(IperfTCPProfile())
registry.register(IperfJitterProfile())
