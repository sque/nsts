'''
Created on Nov 4, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import random
import base


class DummyTestServer(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(DummyTestServer, self).__init__(owner)
        
    def is_supported(self):
        return True
    
    def prepare(self):
        return True
    
    def run(self):
        self.results = random.random()
        self.logger.debug("Results are generated. sending them to client.")
        self.propagate_results()

    def cleanup(self):
        pass
    
class DummyTestClient(base.SpeedTestExecutor):
    
    def __init__(self, owner):
        super(DummyTestClient, self).__init__(owner)
        
    def is_supported(self):
        return True
    
    def prepare(self):
        return True
    
    def run(self):
        self.collect_results()

    def cleanup(self):
        return True
    
class DummyTest(base.SpeedTest):
    def __init__(self):
        super(DummyTest, self).__init__("dummy", "Dummy SpeedTest", DummyTestClient, DummyTestServer)

    

base.enable_test(DummyTest)