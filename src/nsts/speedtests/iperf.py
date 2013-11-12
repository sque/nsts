'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import time
import base
from nsts import units
from subprocess import SubProcessExecutorBase

        
class IperfExecutorSender(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(IperfExecutorSender, self).__init__(owner, 'iperf')
        self.server_arguments = ["-s"]
        self.client_arguments = ["-t" "5", "-y", "C"]
        
    def prepare(self):
        return True
    
    def parse_and_store_output(self):
        output = self.get_subprocess_output()
        self.store_result('transfer_rate', units.BitRateUnit(float(output.split(',')[8])))
        
    def run(self):
        self.send_msg("STARTSERVER",  {"server_arguments" : self.server_arguments})
        self.wait_msg_type('OK')
        self.execute_subprocess("-c", self.connection.remote_addr, *self.client_arguments)
        
        while self.is_subprocess_running():
            time.sleep(0.2)
            
        self.logger.debug("iperf stopped running.")
        self.send_msg("STOPSERVER")
        self.wait_msg_type("OK")
        
        # Parse output
        self.parse_and_store_output()
        self.propagate_results()

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

class IperfJitterExecutorSender(IperfExecutorSender):
    
    def __init__(self, owner):
        super(IperfJitterExecutorSender, self).__init__(owner)
        self.server_arguments = ["-s", "-u"]
        self.client_arguments = ["-u", "-t" "5", "-y", "C"]
        
    def parse_and_store_output(self):
        output = self.get_subprocess_output().split("\n")
        
        #sent = output[0].split(',')
        received = output[1].split(',')
        self.store_result('transfer_rate', units.BitRateUnit(received[8]))
        self.store_result('jitter', units.TimeUnit(received[9] + "ms"))
        self.store_result('lost_packets', units.PacketUnit(received[10]))
        self.store_result('total_packets', units.PacketUnit(received[11]))
        self.store_result('percentage_lost', units.PercentageUnit(received[12]))

class IperfTCP(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultValueDescriptor("transfer_rate", "Transfer Rate", units.BitRateUnit)
        ]
        super(IperfTCP, self).__init__("iperf_tcp", "TCP (iperf)", IperfExecutorSender, IperfExecutorReceiver, descriptors)

class IperfJitter(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultValueDescriptor("transfer_rate", "Trans. Rate", units.BitRateUnit),
                base.ResultValueDescriptor("jitter", "Jitter", units.TimeUnit),
                base.ResultValueDescriptor("lost_packets", "Lost Pck", units.PacketUnit),
                base.ResultValueDescriptor("total_packets", "Total Pck", units.PacketUnit),
                base.ResultValueDescriptor("percentage_lost", "Lost Pck %", units.PercentageUnit)
        ]
        super(IperfJitter, self).__init__("iperf_jitter", "Jitter (iperf)", IperfJitterExecutorSender, IperfExecutorReceiver, descriptors)

base.enable_test(IperfTCP)
base.enable_test(IperfJitter)
