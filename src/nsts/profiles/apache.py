'''
Created on Nov 6, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''
import time
import random
import hashlib
import os
import signal
import re
from nsts.profiles.base import SpeedTestRuntimeError, Profile
from nsts import units, utils
from subprocess import SubProcessExecutorBase


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

    @property
    def pid_file(self):
        return "/tmp/nsts-apache-{0}.pid".format(self.execution_id)

    @property
    def error_log_file(self):
        return "/tmp/nsts-apache-error-{0}.log".format(self.execution_id)

    @property
    def access_log_file(self):
        return "/tmp/nsts-apache-access-{0}.log".format(self.execution_id)

    @property
    def document_root(self):
        return "/tmp/nsts-apache-root-{0}".format(self.execution_id)

    def start_apache(self):

        # Prepare apache arguments
        extra_arguments = list(self.apache_basic_options)
        extra_arguments.append("PidFile {0}".format(self.pid_file))
        extra_arguments.append(
            'LogFormat "%h %l %u %t \\"%r\\" %>s %b \\"%{Referer}'
            'i\\" \\"%{User-agent}i\\"" combined')
        extra_arguments.append("ErrorLog {0}".format(self.error_log_file))
        extra_arguments.append(
            "CustomLog {0} combined".format(self.access_log_file))
        extra_arguments.append(
            "DocumentRoot {0}".format(self.document_root))
        extra_arguments.append(
            "Listen {0}".format(self.context.options['port']))

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
        if not os.path.isfile(self.pid_file):
            raise SpeedTestRuntimeError(
                "There is no PID file {0}".format(self.pid_file))

        # Stopping apache
        pid = int(open(self.pid_file, "r").read().strip())
        self.logger.debug(
            "Found PID {0} in pid file, sending SIGTERM signal".format(pid))
        os.kill(pid, signal.SIGTERM)

        while utils.check_pid(pid):
            time.sleep(0.2)
        self.apache_running = False

    def prepare(self):
        # Generate execution id
        sha1 = hashlib.sha1()
        sha1.update(str(random.random()) + str(time.time()))
        self.execution_id = sha1.hexdigest()

        # Create document root
        os.mkdir(self.document_root)

    def generate_root_file(self, filename, filesize):
        self.logger.debug(
            "Generating document {0} with size {1}".format(filename, filesize))
        with open(os.path.join(self.document_root, filename), "w") as f:
            chunk_size = 1024 * 1024
            written_size = 0
            while written_size < filesize:
                f.write(os.urandom(chunk_size))
                if filesize - written_size < chunk_size:
                    chunk_size = filesize - written_size
                written_size += chunk_size

    def clear_root(self):
        self.logger.debug("Request to empty document root.")
        if not os.path.isdir(self.document_root):
            return
        for filename in os.listdir(self.document_root):
            os.unlink(os.path.join(self.document_root, filename))

    def run(self):
        # Start server
        self.wait_msg_type("STARTSERVER")
        self.start_apache()
        self.send_msg("OK")

        # Generate random files as requested by client
        while True:
            msg = self.wait_msg_type("GENERATEFILE")
            if msg.params['size'] == 0:
                break
            self.clear_root()
            self.generate_root_file(msg.params['filename'], msg.params['size'])
            time.sleep(1)
            self.send_msg("OK")

        self.stop_apache()
        self.send_msg("OK")

        # Collect results
        self.collect_results()

    def cleanup(self):
        self.logger.debug("Cleaning up everything!")
        self.stop_apache()

        # Cleaning up files
        if os.path.isfile(self.pid_file):
            os.unlink(self.pid_file)
        if os.path.isfile(self.error_log_file):
            os.unlink(self.error_log_file)
        if os.path.isfile(self.access_log_file):
            os.unlink(self.access_log_file)

        self.clear_root()
        if os.path.isdir(self.document_root):
            os.rmdir(self.document_root)


class WgetExecutorClient(SubProcessExecutorBase):

    def __init__(self, owner):
        super(WgetExecutorClient, self).__init__(owner, 'wget')
        self.basic_argumnets = [
            "--no-cache",
            "-O", "/dev/null"]

    def parse_output(self):
        output = self.get_subprocess_output()
        rate_line = output.split("\n")[-3]
        self.logger.debug("Parsing wget line > {0}".format(rate_line))

        pattern = re.compile('^[^\(]+\(([^\)]+)\).*$')
        match = pattern.match(rate_line)
        if not match:
            raise SpeedTestRuntimeError("Cannot parse wget output.")

        speed = units.ByteRate(match.group(1))
        return speed

    def url_for(self, filename):
        return self.url_base + filename

    def download_file(self, filename):
        self.logger.debug("Request to download file {0}".format(filename))
        self.execute_subprocess(self.url_for(filename), *self.basic_argumnets)
        while self.is_subprocess_running():
            time.sleep(0.5)
        self.logger.debug("Download finished")
        return self.parse_output()

    def run(self):
        self.send_msg("STARTSERVER")
        self.wait_msg_type("OK")

        filesize = self.context.options['filesize'].raw_value

        if (self.context.options['mode'] == 'time'):
            # Run wget on incremental sizes
            count = 0
            while True:
                filename = "file_{0}".format(count)
                self.send_msg(
                    "GENERATEFILE",
                    {'filename': filename, 'size': filesize})
                self.wait_msg_type('OK')
                speed = self.download_file(filename)

                # Ensure that the achieved speed was 10 times
                # smaller than file size or reached max file size
                downloadtime = self.context.options['downloadtime'].raw_value
                if filesize >= downloadtime or\
                        speed.raw_value < (filesize / downloadtime):
                    break
                self.logger.debug("Downloaded {0} bytes with {1} speed".format(
                    filesize, speed))

                # Calculate new filesize and ensure
                # that we don't exceeded cap size
                filesize = min(
                    int(speed.raw_value * downloadtime * 1.5),
                    self.context.options['maxfilesize'].raw_value)
                self.logger.debug("Increased file_size to  {0} bytes".format(
                    filesize, speed))
                count += 1
        else:
            filename = "file_static"
            self.send_msg(
                "GENERATEFILE",
                {'filename': filename, 'size': filesize})
            self.wait_msg_type('OK')
            speed = self.download_file(filename)

        self.store_result('transfer_rate', speed)

        # Stop server
        self.send_msg("GENERATEFILE", {'size': 0})
        self.wait_msg_type("OK")

        # Propagate results
        self.propagate_results()

    def prepare(self):
        host = self.context.connection.remote_addr
        if self.context.connection.is_ipv6():
            host = "[{0}]".format(self.context.connection.remote_addr)
        else:
            host = self.context.connection.remote_addr
        self.url_base = "http://{remote}:{port}/".format(
            remote=host, port=self.context.options['port'])

    def is_supported(self):
        return SubProcessExecutorBase.is_supported(self)

    def cleanup(self):
        SubProcessExecutorBase.cleanup(self)

p = Profile(
    "apache", "HTTP (apache)", ApacheExecutorServer, WgetExecutorClient,
    "Measure the performance of HTTP, by setting up a "
    "sandboxed apache server and download arbitrary binary files.")
p.add_result("transfer_rate", "TransferRate", units.ByteRate)
p.supported_options.add_option(
    "port", "Apache listen port",
    unit_type=int, default=58338)
p.supported_options.add_option(
    'mode', '"size" to download a specific filesize,'
    ' "time" to download for a specified period',
    unit_type=str, default='size')
p.supported_options.add_option(
    "filesize", "The size of file to download (size mode), "
    "or the initial filesize to try.(time mode)",
    unit_type=units.Byte, default="1 Mbyte")
p.supported_options.add_option(
    "maxfilesize", "The maximum filesize to download (time mode)",
    unit_type=units.Byte, default="100 Mbyte")
p.supported_options.add_option(
    'downloadtime', 'Minimum time to download a continuous file (time mode)',
    unit_type=units.Time, default='10 sec')
