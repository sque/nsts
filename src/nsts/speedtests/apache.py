'''
Created on Nov 6, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''
import time, random, hashlib, os, signal
from nsts.speedtests import base
from nsts import units
from subprocess import SubProcessExecutorBase
import re

HTTP_PORT=58338

class ApacheExecutorServer(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(ApacheExecutorServer, self).__init__(owner, '/usr/sbin/apache2')
        self.apache_basic_options = [
            "HostnameLookups Off",
            "KeepAlive On",
            "MaxKeepAliveRequests 100",
            "KeepAliveTimeout 5"
            ]
        self.execution_id = None
        self.apache_running = False

    def pid_file(self):
        return "/tmp/nsts-apache-{0}.pid".format(self.execution_id)
    
    def error_log_file(self):
        return "/tmp/nsts-apache-error-{0}.log".format(self.execution_id)
    
    def document_root(self):
        return "/tmp/nsts-apache-root-{0}".format(self.execution_id)
    
    def start_apache(self):

        # Prepare apache arguments
        extra_arguments = list(self.apache_basic_options)
        extra_arguments.append("PidFile {0}".format(self.pid_file()))
        extra_arguments.append("ErrorLog {0}".format(self.error_log_file()))
        extra_arguments.append("DocumentRoot {0}".format(self.document_root()))
        extra_arguments.append("Listen {0}".format(HTTP_PORT))
        
        apache_arguments = ["-d", "/tmp"]
        for opt in extra_arguments:
            apache_arguments.append("-c")
            apache_arguments.append(opt)
        
        # Start apache
        self.logger.debug("Starting apache server")
        self.execute_subprocess(*apache_arguments)
        
        # Wait for apache to begin
        while self.is_subprocess_running():
            time.sleep(0.2)
        self.apache_running = True
        self.logger.debug("Apache server started")
        
    def stop_apache(self):
        if not self.apache_running:
            return
        
        self.logger.debug("Stopping apache server gracefully.")
        if not os.path.isfile(self.pid_file()):
            raise base.SpeedTestRuntimeError("There is no PID file {0}".format(self.pid_file()))
        
        # Stopping apache
        pid = int(open(self.pid_file(), "r").read().strip())
        self.logger.debug("Found PID {0} in pid file, sending SIGTERM signal".format(pid))
        os.kill(pid, signal.SIGTERM)
        
        self.apache_running = False
        
    def prepare(self):
        # Generate execution id
        sha1 = hashlib.sha1()
        sha1.update(str(random.random()) + str(time.time()))
        self.execution_id = sha1.hexdigest()
        
        # Create document root
        os.mkdir(self.document_root())
        with open(os.path.join(self.document_root(), "file_1M"), "w") as f:
            f.write(os.urandom(1024*1024))
        
    def run(self):
        # Start server
        self.wait_msg_type("STARTSERVER")
        self.start_apache()
        self.send_msg("OK")
    
        # Stop server
        self.wait_msg_type("STOPSERVER")
        self.stop_apache()
        self.send_msg("OK")
        
        # Collect results
        self.collect_results()
    
    def cleanup(self):
        self.stop_apache()
        
        # Cleaning up files
        if os.path.isfile(self.pid_file()):
            os.unlink(self.pid_file())
        if os.path.isfile(self.error_log_file()):
            os.unlink(self.error_log_file())

class WgetExecutorClient(SubProcessExecutorBase):
    
    def __init__(self, owner):
        super(WgetExecutorClient, self).__init__(owner, 'wget')
        self.basic_argumnets = [
                "--no-cache",
                "-O", "/dev/null",
                "--report-speed=bits"
                ]

    def parse_output(self):
        output = self.get_subprocess_output()
        rate_line = output.split("\n")[-3]
        self.logger.debug("Parsing wget line > {0}".format(rate_line))
        
        pattern = re.compile('^[^\(]+\(([^\)]+)\).*$')
        match = pattern.match(rate_line)
        if not match:
            raise base.SpeedTestRuntimeError("Cannot parse wget output.")
        
        speed = units.BitRateUnit()
        speed.parse(match.group(1))
        return speed
        
    def url_for(self, file):
        return self.url_base + file
    
    def run(self):
        self.send_msg("STARTSERVER")
        self.wait_msg_type("OK")
        
        # Run wget 
        self.execute_subprocess(self.url_for("file_1M"), *self.basic_argumnets)
        while self.is_subprocess_running():
            time.sleep(0.5)
            
        speed = self.parse_output()
        self.store_result('transfer_rate', speed)

        # Stop server
        self.send_msg("STOPSERVER")
        self.wait_msg_type("OK")
        
        # Propagate results
        self.propagate_results()
        
    
    def prepare(self):
        self.url_base = "http://{remote}:{port}/".format(remote = self.connection.remote_ip, port = HTTP_PORT)
    
    def is_supported(self):
        return True
    
    def cleanup(self):
        return True

class ApacheTest(base.SpeedTest):
    
    def __init__(self):
        descriptors = [
                base.ResultEntryDescriptor("transfer_rate", "TransferRate", units.BitRateUnit),
        ]
        super(ApacheTest, self).__init__("apache", "HTTP (apache)", WgetExecutorClient, ApacheExecutorServer, descriptors)

base.enable_test(ApacheTest)
