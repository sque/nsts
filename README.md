Network SpeedTest Suite
=======================

NSTS is meta-benchmarking network speed test suite to estimate network performance.
It is a tool to create benchmark profiles that can be used to standardize
and ease the network benchmarking. The suite knows how to execute
benchmarking tools or real scenario network services and monitor their performance.  


Dependencies
------------
NSTS is written in pure Python 2.7 and has no external module dependencies.
Though the following modules are optional [numpy](http://www.numpy.org/)

Usage
-----
After downloading and unzipping the software you can run NSTS by executing
`python nsts.py --help`

To run NSTS you have to run the server in one endpoint and the client
in the other endpoint of the link that you want to benchmark.

Examples
--------

Execute server in one endpoint
`python nsts.py -s`

Run TCP,ping profiles bidirectional
`python nsts.py -c server.address.com --tests=iperf_tcp,ping`

Run TCP and Jitter profiles only on transmission
`python nsts.py -c server.address.com --tests=iperf_tcp-s,ping-s`