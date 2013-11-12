
from __future__ import absolute_import
import unittest
from nsts.speedtests.base import ExecutionDirection, ResultValueDescriptor, OptionValueDescriptor
from nsts import units


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