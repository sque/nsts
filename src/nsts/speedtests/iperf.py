'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import subprocess as proc, time
import base
from nsts import utils, units

class IperfExecutorBase(base.SpeedTestExecutor):

    def __init__(self, owner):
        super(IperfExecutorBase, self).__init__(owner)
        self.iperf_executable = utils.which('iperf')
        self.iperf_process = None
    
    def execute_iperf(self, *extra_args):
        args = [self.iperf_executable]
        args.extend(extra_args)
        self.logger.debug("Executing iperf - {0}.".format(args))
        self.iperf_process = proc.Popen(args, stdout = proc.PIPE)
        
    def is_supported(self):
        return self.iperf_executable is not None
    
    def is_iperf_running(self):
        if self.iperf_process is None:
            return False
        
        self.iperf_process.poll()
        return self.iperf_process.returncode is None
    
    def kill_iperf(self):
        self.logger.debug("Request to kill iperf")
        if not self.is_iperf_running():
            return False
        
        self.iperf_process.kill()
        self.iperf_process = None
        
    def get_iperf_output(self):
        if self.iperf_process is None:
            return False

        (output, _) = self.iperf_process.communicate()
        return output

    def cleanup(self):
        self.kill_iperf()
        self.iperf_process = None
        
class IperfExecutorClient(IperfExecutorBase):
    
    def __init__(self, owner):
        super(IperfExecutorClient, self).__init__(owner)
        self.server_arguments = ["-s"]
        self.client_arguments = ["-t" "5", "-y", "C"]
        
    def prepare(self):
        return True
    
    def parse_and_store_output(self):
        output = self.get_iperf_output()
        self.store_result('transfer_rate', units.BitRateUnit(float(output.split(',')[8])))
        
    def run(self):
        self.send_msg("STARTSERVER",  self.server_arguments)
        self.wait_msg_type('OK')
        self.execute_iperf("-c", self.connection.remote_ip, *self.client_arguments)
        
        while self.is_iperf_running():
            time.sleep(0.2)
            
        self.logger.debug("iperf stopped running.")
        self.send_msg("STOPSERVER")
        self.wait_msg_type("OK")
        
        # Parse output
        self.parse_and_store_output()
        self.propagate_results()
    
class IperfJitterExecutorClient(IperfExecutorClient):
    
    def __init__(self, owner):
        super(IperfExecutorClient, self).__init__(owner)
        self.server_arguments = ["-s", "-u"]
        self.client_arguments = ["-u", "-t" "5", "-y", "C"]
        
    def parse_and_store_output(self):
        output = self.get_iperf_output().split("\n")
        
        sent = output[0].split(',')
        received = output[1].split(',')
        self.store_result('transfer_rate', units.BitRateUnit(float(received[8])))
        self.store_result('jitter', units.TimeUnit(float(received[9])))
        self.store_result('lost_packets', units.PacketUnit(float(received[10])))
        self.store_result('total_packets', units.PacketUnit(float(received[11])))
        self.store_result('percentage_lost', units.PercentageUnit(float(received[12])))
    
        
class IperfExecutorServer(IperfExecutorBase):
    
    def __init__(self, owner):
        super(IperfExecutorServer, self).__init__(owner)
        
    def prepare(self):
        return True
    
    def run(self):
        msg = self.wait_msg_type("STARTSERVER")
        self.execute_iperf(*msg.params)
        time.sleep(0.2)
        self.send_msg("OK")

        self.wait_msg_type("STOPSERVER")
        self.kill_iperf()
        self.send_msg("OK")
        
        # Collect __results
        self.collect_results()


class IperfTCPSend(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("transfer_rate", "Transfer Rate", units.BitRateUnit)
        ]
        super(IperfTCPSend, self).__init__("iperf_tcp_send", "TCP send (iperf)", IperfExecutorClient, IperfExecutorServer, descriptors)


class IperfTCPReceive(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("transfer_rate", "Transfer Rate", units.BitRateUnit)
        ]
        super(IperfTCPReceive, self).__init__("iperf_tcp_receive", "TCP receive (iperf)", IperfExecutorServer, IperfExecutorClient, descriptors)

class IperfJitterSend(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("transfer_rate", "Trans. Rate", units.BitRateUnit),
                base.ResultEntryDescriptor("jitter", "Jitter", units.TimeUnit),
                base.ResultEntryDescriptor("lost_packets", "Lost Pck", units.PacketUnit),
                base.ResultEntryDescriptor("total_packets", "Total Pck", units.PacketUnit),
                base.ResultEntryDescriptor("percentage_lost", "Lost Pck %", units.PercentageUnit)
        ]
        super(IperfJitterSend, self).__init__("iperf_jitter_send", "Jitter send (iperf)", IperfJitterExecutorClient, IperfExecutorServer, descriptors)

class IperfJitterReceive(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("transfer_rate", "Trans. Rate", units.BitRateUnit),
                base.ResultEntryDescriptor("jitter", "Jitter", units.TimeUnit),
                base.ResultEntryDescriptor("lost_packets", "Lost Pck", units.PacketUnit),
                base.ResultEntryDescriptor("total_packets", "Total Pck", units.PacketUnit),
                base.ResultEntryDescriptor("percentage_lost", "Lost Pck %", units.PercentageUnit)
        ]
        super(IperfJitterReceive, self).__init__("iperf_jitter_receive", "Jitter receive (iperf)", IperfExecutorServer, IperfJitterExecutorClient, descriptors)
        
base.enable_test(IperfTCPSend)
base.enable_test(IperfTCPReceive)
base.enable_test(IperfJitterSend)
base.enable_test(IperfJitterReceive)