'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import random
from nsts.tests import base


class DummyTestServer(base.TestExecutor):
    
    def __init__(self, owner):
        super(DummyTestServer, self).__init__(owner)
        
    def prepare(self):
        return True
    
    def run(self):
        self.results = random.random()
        self.logger.debug("Results are generated. sending them to client.")
        self.propagate_results()

    def cleanup(self):
        pass
    
class DummyTestClient(base.TestExecutor):
    
    def __init__(self, owner):
        super(DummyTestClient, self).__init__(owner)
        
    def prepare(self):
        return True
    
    def run(self):
        self.collect_results()

    def cleanup(self):
        return True
    
class DummyTest(base.Test):
    def __init__(self):
        super(DummyTest, self).__init__("dummy", "Dummy Test", DummyTestClient, DummyTestServer)
        
    def is_supported(self):
        return True
    

base.enable_test(DummyTest)