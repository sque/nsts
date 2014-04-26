'''
@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

import unittest
from nsts import events
from nsts.events import dispatcher

class TestReceiver(object):
    
    def __init__(self):
        self.calls = []
        
    def __call__(self, n):
        assert isinstance(n, events.Notification)
        self.calls.append(n)
    
class TestEvents(unittest.TestCase):


    def testSendEmpty(self):
        
        d = events.Dispatcher()
        # send new
        d.send("test_event")


    def testCallbacks(self):
        
        d = events.Dispatcher()
        r1 = TestReceiver()
        r2 = TestReceiver()
        d.connect("event1", r1)
        d.connect("event2", r2)
        d.connect("all", r2)
        d.connect("all", r1)
        
        self.assertEquals(0, len(r1.calls))
        self.assertEquals(0, len(r2.calls))
        
        d.send("unknown_event")
        self.assertEquals(0, len(r1.calls))
        self.assertEquals(0, len(r2.calls))
        
        d.send("event1")
        self.assertEquals(0, len(r2.calls))
        self.assertEquals(1, len(r1.calls))
        self.assertEquals(r1.calls[0].event_name, "event1")
        self.assertEquals(r1.calls[0].sender, None)
        self.assertEquals(r1.calls[0].extra, {})
        
        d.send("event2", sender="bla", param="hey")
        self.assertEquals(1, len(r2.calls))
        self.assertEquals(1, len(r1.calls))
        self.assertEquals(r2.calls[0].event_name, "event2")
        self.assertEquals(r2.calls[0].sender, "bla")
        self.assertEquals(r2.calls[0].extra, {"param" : "hey"})
        
        d.send("all", sender="hik", another="hok")
        self.assertEquals(2, len(r2.calls))
        self.assertEquals(2, len(r1.calls))
        self.assertEquals(r1.calls[1].event_name, "all")
        self.assertEquals(r1.calls[1].sender, "hik")
        self.assertEquals(r1.calls[1].extra, {"another" : "hok"})
        self.assertEquals(r2.calls[1].event_name, "all")
        self.assertEquals(r2.calls[1].sender, "hik")
        self.assertEquals(r2.calls[1].extra, {"another" : "hok"})
        
    def testGlobalDispacher(self):
        
        r1 = TestReceiver()
        dispatcher.connect("event1", r1)
        
        self.assertEquals(0, len(r1.calls))
        
        dispatcher.send("unknown_event")
        self.assertEquals(0, len(r1.calls))
        
        dispatcher.send("event1")
        self.assertEquals(1, len(r1.calls))
        self.assertEquals(r1.calls[0].event_name, "event1")
        self.assertEquals(r1.calls[0].sender, None)
        self.assertEquals(r1.calls[0].extra, {})
        