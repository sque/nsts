
Network Speed Test Suite (NSTS) Protocol
========================================

1. Description
=================================
It is an a plain-text protocol that is used
by NSTS to manage execution of tests and
 collection of results between the peers.
 
 
2. Format
=================================

All informations are exchanged in the form
of messages. Each message is separated
by the next message by using the LF (LineFeed)
character.

Each message has the following format
<TYPE> <PARAMS>

TYPE: Is a sequence of \[A-Z0-9\] characters
      that define the type of message.
PARAMS: Is a base64 encoded of the payload
      that is generated by python pickle text
      format.
      
2.0 "OK"
---------------------------------
PARAMS = {
   }
A reply that last message was received
and executed successfully.

2.1 "CHECKTEST"
--------------------------------- 
PARAMS = {
   "name" // (string) unique name of the test
   }
Asks the other peer to check for a test. Checking
involves if it has the test or it can be run
on the specific target.

A "TESTINFO" response is expected.

2.2 "TESTINFO"
---------------------------------
PARAMS = {
   "name" 			// (string) unique name of the test
   "installed" 		// (bool) Flag if the test is known
   "supported"		// (bool) Flag if the test can be run
   "error"			// (string) Any error message why is not supported 
}
A message containing information about the status
of test. 

2.3 "PREPARETEST"
---------------------------------
PARAMS = {
	"name"			// (string) unique name of the test
}
Requests the other end to prepare a test for
execution. An OK reply is expected.

2.4 "STARTTEST"
---------------------------------
PARAMS = {
	"name"			// (string) unique name of the test
}
Request to start execution of the test. An OK reply is expected.

2.5 "TESTFINISHED"
---------------------------------
PARAMS = {
	"name"			// (string) unique name of the test
}
Annouce that test has finished.

2.6 "COLLECTOUTPUT"
---------------------------------
PARAMS = {
	"name"			// (string) unique name of the test
}
Request to collect output results form the test.
An OUTPUT reply is expected.

2.7 "OUTPUT"
---------------------------------
PARAMS = {
	"name"			// (string) unique name of the test
	"output"		// (xxxxx) output that the test plugin can understand
}

2.8 "__XXXXX_YYYYY"
---------------------------------
If a test needs to intercommunicate it can
send custom message. The type of the message must be in the 
form of 

__XXXX_YYYYY where 
XXXX is the unique name of the test
YYYY is a test defined identifier for the message type