
from __future__ import absolute_import
import unittest
from nsts.speedtests.base import ExecutionDirection, ResultValueDescriptor, \
    OptionValueDescriptor, SpeedTestExecutor, SpeedTestDescriptor
from nsts import units
from nsts.proto import NSTSConnectionBase
import socket

class SpeedTestExecutorA(SpeedTestExecutor):
    pass
class SpeedTestExecutorB(SpeedTestExecutor):
    pass

class TestExecutionDirection(unittest.TestCase):
    
    def test_constructor(self):
        
        # Check empty constructor
        with self.assertRaises(TypeError):
            ExecutionDirection()
        
        # Check wrong names
        with self.assertRaises(ValueError):
            ExecutionDirection("la")
            
        with self.assertRaises(ValueError):
            ExecutionDirection("sen")
        
        with self.assertRaises(ValueError):
            ExecutionDirection("rec")
            
            
        # Valid constructors
        ExecutionDirection("s")
        ExecutionDirection("send")
        ExecutionDirection("r")
        ExecutionDirection("receive")
        
    def test_is_func(self):
        d = ExecutionDirection("s")
        self.assertTrue(d.is_send())
        self.assertFalse(d.is_receive())
        d = ExecutionDirection("s")
        self.assertTrue(d.is_send())
        self.assertFalse(d.is_receive())
        
        d = ExecutionDirection("r")
        self.assertFalse(d.is_send())
        self.assertTrue(d.is_receive())
        d = ExecutionDirection("receive")
        self.assertFalse(d.is_send())
        self.assertTrue(d.is_receive())

    def test_opposite(self):
        d = ExecutionDirection("s")
        o = d.opposite()
        
        self.assertIsInstance(o, ExecutionDirection)
        self.assertFalse(o.is_send())
        self.assertTrue(o.is_receive())
        
        d = ExecutionDirection("r")
        o = d.opposite()
        
        self.assertIsInstance(o, ExecutionDirection)
        self.assertTrue(o.is_send())
        self.assertFalse(o.is_receive())
        
class TestResultValueDescriptor(unittest.TestCase):
    
    def test_constructor(self):
        # Cannot omit parameters
        with self.assertRaises(TypeError):
            ResultValueDescriptor()
        
        # Assert on types
        with self.assertRaises(TypeError):
            ResultValueDescriptor('a','a', float)
            
        ResultValueDescriptor('myid','myname', units.TimeUnit)
        ResultValueDescriptor(1,'', units.BitRateUnit)
        
    def test_properties(self):
        
        r = ResultValueDescriptor('myid','myname', units.TimeUnit)
        self.assertEqual(r.id, 'myid')
        self.assertEqual(r.name, 'myname')
        self.assertEqual(r.unit_type, units.TimeUnit)
        
        r = ResultValueDescriptor(1,'', units.BitRateUnit)
        self.assertEqual(r.id, 1)
        self.assertEqual(r.name, '')
        self.assertEqual(r.unit_type, units.BitRateUnit)
        
class TestOptionValueDescriptor(unittest.TestCase):
    
    def test_constructor(self):
        # Cannot omit parameters
        with self.assertRaises(TypeError):
            OptionValueDescriptor()
        
        
        OptionValueDescriptor('a','a', float)
        OptionValueDescriptor('myid','myhelp', units.TimeUnit)
        OptionValueDescriptor(1,'', units.BitRateUnit)
        
    def test_properties(self):
        
        o = OptionValueDescriptor('myid','myhelp', units.TimeUnit)
        self.assertEqual(o.id, 'myid')
        self.assertEqual(o.help, 'myhelp')
        self.assertEqual(o.type, units.TimeUnit)
        
        o = OptionValueDescriptor(1,'', float)
        self.assertEqual(o.id, '1')
        self.assertEqual(o.help, '')
        self.assertEqual(o.type, float)
        
class TestSpeedTestExecutor(unittest.TestCase):
    
    def test_constructor(self):
        
        # Cannot omit parameters
        with self.assertRaises(TypeError):
            SpeedTestExecutor()
        
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        SpeedTestExecutor(d)
        
        with self.assertRaises(TypeError):
            SpeedTestExecutor(1)

    def test_properties(self):
        
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        e = SpeedTestExecutor(d)
        
        self.assertEqual(d, e.owner)
        self.assertIsNone(e.connection)
        self.assertEquals(len(e.results), 0)
        
    def test_initialize(self):
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        e = SpeedTestExecutor(d)
        
        self.assertIsNone(e.connection)
        c = NSTSConnectionBase(socket.socket())
        e.initialize(c)
        self.assertEqual(c, e.connection)
        
    def test_store_result(self):
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        e = SpeedTestExecutor(d)
        
        with self.assertRaises(ValueError):
            e.store_result('smt', 'a')
            
        d.add_result('smt', 'Something', units.TimeUnit)
        d.add_result('smt2', 'Something', units.TimeUnit)
        d.add_result('smt3', 'Something', units.TimeUnit)
        
        e = SpeedTestExecutor(d)
        self.assertEqual(len(e.results), 3)
        self.assertIsNone(e.results['smt'])
        self.assertIsNone(e.results['smt2'])
        self.assertIsNone(e.results['smt3'])

        
        # Check casting for storing
        e.store_result('smt', 0)
        self.assertEqual(e.results['smt'], units.TimeUnit(0))
        
        # Overwrite values
        e.store_result('smt', '15 hour')
        self.assertNotEqual(e.results['smt'], units.TimeUnit(0))
        self.assertEqual(e.results['smt'], units.TimeUnit('15 hour'))
    
    def test_result_order(self):
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        d.add_result('smt1', 'Something', units.TimeUnit)
        d.add_result('smt2', 'Something', units.TimeUnit)
        d.add_result('smt3', 'Something', units.TimeUnit)
        e = SpeedTestExecutor(d)
        
        # Check order
        self.assertEqual(['smt1', 'smt2', 'smt3'], e.results.keys())
        
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        d.add_result('smt3', 'Something', units.TimeUnit)
        d.add_result('smt2', 'Something', units.TimeUnit)
        d.add_result('smt1', 'Something', units.TimeUnit)
        e = SpeedTestExecutor(d)
        
        # Check order
        self.assertEqual(['smt3', 'smt2', 'smt1'], e.results.keys())
        
    def test_unimplemented(self):
        d = SpeedTestDescriptor('d', 'd', SpeedTestExecutor, SpeedTestExecutor)
        e = SpeedTestExecutor(d)
        
        with self.assertRaises(NotImplementedError):
            e.prepare()
            
        with self.assertRaises(NotImplementedError):
            e.is_supported()
            
        with self.assertRaises(NotImplementedError):
            e.run()
            
        with self.assertRaises(NotImplementedError):
            e.cleanup()
            

class TestSpeedTestDescriptor(unittest.TestCase):
    
    def test_constructor(self):
        with self.assertRaises(TypeError):
            SpeedTestDescriptor()
            
        with self.assertRaises(TypeError):
            SpeedTestDescriptor('myid', 'myname', SpeedTestExecutor, float)
            
        with self.assertRaises(TypeError):
            SpeedTestDescriptor('myid', 'myname', float, SpeedTestExecutor)
        
        SpeedTestDescriptor('myid', 'myname', SpeedTestExecutor, SpeedTestExecutor)
        
    def test_properties(self):
        
        d = SpeedTestDescriptor('myid', 'myname', SpeedTestExecutorA, SpeedTestExecutorB)
        
        self.assertEqual(d.id, 'myid')
        self.assertEqual(d.name, 'myname')
        self.assertEqual(d.send_executor_class , SpeedTestExecutorA)
        self.assertEqual(d.receive_executor_class, SpeedTestExecutorB)
        self.assertIsNotNone(d.supported_options)
        self.assertIsNotNone(d.supported_results)
        
    def test_options(self):
        self.assertTrue(False, 'not implemented yet')