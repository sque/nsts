from __future__ import absolute_import
import unittest

from nsts.options import OptionValueDescriptor, OptionsDescriptor, Options, UnknownOptionError
from nsts import units

class TestOptionValueDescriptor(unittest.TestCase):
    
    def test_constructor(self):
        # Cannot omit parameters
        with self.assertRaises(TypeError):
            OptionValueDescriptor()
        
        
        OptionValueDescriptor('a','a', float)
        OptionValueDescriptor('myid','myhelp', units.TimeUnit)
        OptionValueDescriptor(1,'', units.BitRateUnit)
        OptionValueDescriptor(1,'', units.BitRateUnit, default = 1)
        
    def test_properties(self):
        
        o = OptionValueDescriptor('myid','myhelp', units.TimeUnit)
        self.assertEqual(o.id, 'myid')
        self.assertEqual(o.help, 'myhelp')
        self.assertEqual(o.type, units.TimeUnit)
        self.assertEqual(o.default, None)
        
        o = OptionValueDescriptor('myid','myhelp', units.TimeUnit, default=0)
        self.assertEqual(o.id, 'myid')
        self.assertEqual(o.help, 'myhelp')
        self.assertEqual(o.type, units.TimeUnit)
        self.assertEqual(o.default, units.TimeUnit(0))
        
        o = OptionValueDescriptor(1,'', float, default=10)
        self.assertEqual(o.id, '1')
        self.assertEqual(o.help, '')
        self.assertEqual(o.type, float)
        self.assertEqual(o.default, 10)
        

class TestCaseExtra(unittest.TestCase):
    
    def assertLength(self, o, size):
        self.assertEqual(len(o), size)
        count = 0
        for i in o:
            count += 1
        self.assertEqual(count, size)
        
class TestOptionDescriptor(TestCaseExtra):
    
    def test_empty_constructor(self):
        
        d = OptionsDescriptor()
        self.assertLength(d, 0)
        
        with self.assertRaises(UnknownOptionError):
            d['test']
    
    def test_add_option(self):
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
                
        self.assertLength(d, 1)
        self.assertEqual(d.supported['test'].type, float)
        self.assertEqual(d.supported['test'].help, 'Hello')
        self.assertEqual(d.supported['test'].id, 'test')
        self.assertEqual(d.supported['test'].default, None)

        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        self.assertLength(d, 2)
        self.assertEqual(d.supported['test2'].type, units.TimeUnit)
        self.assertEqual(d.supported['test2'].help, 'Yeah')
        self.assertEqual(d.supported['test2'].id, 'test2')
        self.assertEqual(d.supported['test2'].default, units.TimeUnit(0))
        
        
    def test_access(self):
        
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        
        with self.assertRaises(UnknownOptionError):
            d['unknown']
            
        # get item access
        self.assertEqual(d['test'].id, 'test')
        self.assertEqual(d['test2'].id , 'test2')
        
        # Iterator access
        optids = []
        ids = []
        for opt_id in d:
            optids.append(opt_id)
            ids.append(d[opt_id].id)
        self.assertEqual(optids, ['test', 'test2'])
        self.assertEqual(ids, ['test', 'test2'])
        
    def test_mutator(self):
        
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        
        with self.assertRaises(TypeError):
            d['unknown'] = 5
        
        with self.assertRaises(TypeError):
            d['test'] = 5
        
        
class TestOptions(TestCaseExtra):
    
    def assertLength(self, o, size):
        self.assertEqual(len(o), size)
        count = 0
        for i in o:
            count += 1
        self.assertEqual(count, size)
    
    def test_empty_constructor(self):
        
        with self.assertRaises(TypeError):
            o = Options()
            
        d = OptionsDescriptor()
        o = Options(d)
        self.assertLength(o, 0)
        
        with self.assertRaises(UnknownOptionError):
            o['test']
        
    def test_add_option(self):
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        o = Options(d)
        
        self.assertLength(o, 1)
        self.assertLength(o.supported, 1)
        self.assertEqual(o.supported['test'].type, float)
        self.assertEqual(o.supported['test'].help, 'Hello')
        self.assertEqual(o.supported['test'].id, 'test')
        self.assertEqual(o.supported['test'].default, None)
        self.assertIsNone(o['test'])
        
        
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        o = Options(d)

        self.assertLength(o, 2)
        self.assertLength(o.supported, 2)
        self.assertEqual(o.supported['test2'].type, units.TimeUnit)
        self.assertEqual(o.supported['test2'].help, 'Yeah')
        self.assertEqual(o.supported['test2'].id, 'test2')
        self.assertEqual(o.supported['test2'].default, units.TimeUnit(0))
        self.assertIsNone(o['test'])
        self.assertEqual(o['test2'], units.TimeUnit(0))
        
    def test_access(self):
        
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        o = Options(d)

        with self.assertRaises(UnknownOptionError):
            o['unknown']
            
        # get item access
        self.assertIsNone(o['test'])
        self.assertEqual(o['test2'], units.TimeUnit(0))
        
        # Iterator access
        optids = []
        values = []
        for opt_id in o:
            optids.append(opt_id)
            values.append(o[opt_id])
        self.assertEqual(optids, ['test', 'test2'])
        self.assertEqual(values, [None, units.TimeUnit(0)])
        
    def test_mutator(self):
        
        d = OptionsDescriptor()
        d.add_option('test', 'Hello', float)
        d.add_option('test2', 'Yeah', units.TimeUnit, 0)
        o = Options(d)
        
        with self.assertRaises(UnknownOptionError):
            o['unknown'] = 5
            
        o['test'] = 5
        self.assertEqual(o['test'], 5)
        
        
        o['test2'] = 7.1
        self.assertEqual(o['test2'], units.TimeUnit(7.1))
        
        # Request for impossible casting
        with self.assertRaises(TypeError):
            o['test2'] = units.BitRateUnit(0)
            
        # Iterator access
        optids = []
        values = []
        for opt_id in o:
            optids.append(opt_id)
            values.append(o[opt_id])
        self.assertEqual(optids, ['test', 'test2'])
        self.assertEqual(values, [5, units.TimeUnit(7.1)])
