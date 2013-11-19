Network SpeedTest Suite
=======================

NSTS is network meta-benchmarking suite, that was created to automate and standardize network performance estimation process, without defining explicit algorithms. As a meta-benchmarking tool it knows how to execute other established benchmarking tools and gather results, or even run real scenario network services and monitor their performance.

Installation
------------
Before installing NSTS ensure that you have python 2.7+ on your system.

Download the latest release of NSTS from https://github.com/sque/nsts/releases, and then unzip it in a folder. You can execute nsts, by executing `nsts.py`
```
cd nsts-latest-release/src
python nsts.py --help
```

Concepts
--------
NSTS uses some terms and concepts to describe benchmarking procedure. It would be best to familiarize yourself before starting using NSTS.

### Profile
Profile is a "wrapper" around other benchmarking tools or network services. A *profile* describes the "wrapped" tool, possible results, profile options and provides the needed scripts to execute it.

### Sampling
Although you could run a profile and gather results, this is not always the best idea. The results have a variance due to system/network state, and other parameters that we cannot control. To overcome this problem, NSTS executes multiple times a profile and return statistical data on the results (average, minimum, maximum, deviation). Every execution of a profile is called a *sample*, and there is a dead-time *interval* between samples.

### Execution Direction
Each profiles define a one way speed test. This means that the one end will transmit data and the other will receive them. When you execute a profile you need to define *direction* of execution, nsts will organize both peers to achieve it.

### Test
A test is a complete description of how to execute a profile in a reprodusable way. It involves *options* of the profile, *direction* of execution, number of *samples*, *interval* time between samples and some other parameters.

### Suite
A test suite, is a list of multiple tests, that can be described a *suite file*. A speed suite provides a way to standardize a benchmarking procedure in a given enviroment. You can have suite that target more on transfer rates, or packet loss, or latency depending the scenarion you want to benchmark.

### Suite File
A suite file is an *ini* file that contains all tests for the given suite. (check "suite syntax" section). Instead of defining test from command line you can pass a suite file to execute.



Usage
-----
After downloading and unzipping the software you can run NSTS by executing
```
python nsts.py --help
```

To run NSTS you have to run the server in one endpoint and the client in the other endpoint of the link that you want to benchmark.

## Example: Get list of installed profiles and their options
```
python nsts.py --list-profiles
```

## Example: Run simple TCP throught

Server:
```
python nsts.py -s
```

Client:
```
python nsts.py -c servername --tests=iperf_tcp
```

## Example: Run transmission latency tests

Server:
```
python nsts.py -s
```

Client:
```
python nsts.py -c servername --tests=iperf_jitter-s,ping-s
```

## Example: Run a suite

Server:
```
python nsts.py -s
```

Client:
```
python nsts.py -c servername --suite=filename.ini
```

## Example: Run on IPv6 and different port

Server:
```
python nsts.py -s -6 -p 15000
```

Client:
```
python nsts.py -6 -p 15000 -c servername --suite=filename.ini
```

Suite Files
-----------
A suite file is an configuration file (ini format) that contains all tests for the given suite. Each section of the *ini* file is a test except section "global" which is used for suite options. The name of each section defines also the `id` of the test so it must be unique inside a suite.


Example:
```ini
[global]
interval = 1 sec
samples = 10

[short_tcp]
profile=iperf_tcp
name = Fast connections
samples = 30
interval = 0
iperf_tcp.min_time = 1 sec

[long_tcp]
profile=iperf_tcp
name = Long last connections 
samples = 5
interval = 20 sec
iperf_tcp.min_time = 20 sec

[low_rate_latency]
name = Low Rate latency jittering
profile=iperf_jitter
samples = 6
interval = 0
iperf_jitter.time = 10
iperf_jitter.rate = 1 Mbps

[fast_rate_latency]
name = Low Rate latency jittering
profile=iperf_jitter
samples = 6
interval = 0
iperf_jitter.time = 10
iperf_jitter.rate = 10 Mbps

[estimate_latency]
name = Latency estimations
profile=ping

```
* **interval**      : Is the time between samples. You can define it globaly and overide its value per test.
* **samples**       : Is the number of profile execution per test. You can define it globaly and overide its value per test.
* **name**          : Is the friendly name of test, it will be shown on the results section
* **profile**       : (mandatory) The id of the profile
* **direction**     : By default tests are run bidirectional. You can define "send" or "receive direction .
* **foo.bar** : Set the **option** *bar* of the **profile** *foo*. Foo is the id of the profile and must be the same as at the **profile** option. **bar** must be an id of a valid option of profile foo.


Feedback
========

Please file your ideas, bugs, comments at https://github.com/sque/nsts
