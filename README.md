Network SpeedTest Suite
=======================

NSTS is meta-benchmarking network speed test suite to estimate network performance. It is a tool to create benchmark profiles that can be used to standarize and ease the network benchmarking. The suite knows how to execute benchmarking tools or real scenario network services and monitor their performance.  


Dependencies
------------
NSTS is written in pure Python 2.7 and depends on the following non standard modules
`numpy` 

Usage
-----
After downloading and unziping the software you can run NSTS by executing
`python nsts.py`

```
usage: nsts.py [-h] (-c CONNECT | -s | --list-tests) [-d DEBUG]
               [--samples SAMPLES] [--sample-interval SAMPLE_INTERVAL]
               [--tests TESTS]

optional arguments:
  -h, --help            show this help message and exit
  -c CONNECT, --connect CONNECT
                        connect to server.
  -s, --server          start in server mode.
  --list-tests          list all available tests.
  -d DEBUG, --debug DEBUG
                        select level of logging. 0 will log everything
                        (default 30)
  --samples SAMPLES     how many times to execute a test (default 1)
  --sample-interval SAMPLE_INTERVAL
                        The interval time between samples in seconds. (default
                        0.0sec)
  --tests TESTS         a comma separated list of all tests to execute

This application was developed for the need of benchmarking wireless links at
heraklion wireless metropolitan network (hwmn.org). If you find a bug please
report it at https://github.com/sque/nsts
```

To run NSTS you have to run the server in one endpoint and the client
in the other endpoint of the link that you want to benchmark.

