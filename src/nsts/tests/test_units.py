
from __future__ import absolute_import
import unittest
from nsts import units

class TestTimeUnit(unittest.TestCase):
    
    def test_emtpy_constructor(self):
        t = units.TimeUnit()
        self.assertEqual(t.raw_value, 0)
        
    def test_number_constructor(self):
        t = units.TimeUnit(1.0)
        self.assertEqual(t.raw_value, 1.0)
        
        t = units.TimeUnit(3)
        self.assertEqual(t.raw_value, 3.0)
        
        t = units.TimeUnit(477777.54)
        self.assertEqual(t.raw_value, 477777.54)

    def test_copy_constructor(self):
        
        t1 = units.TimeUnit(15)
        t2 = units.TimeUnit(t1)
        self.assertEqual(t1, t2)
        self.assertEqual(t2.raw_value, 15)
        
    def test_parse_constructor(self):
        self.assertEqual(units.TimeUnit('0 ms').raw_value, 0)
        self.assertEqual(units.TimeUnit('1 ms').raw_value, 0.001)
        self.assertEqual(units.TimeUnit('1.5 ms').raw_value, 0.0015)
        self.assertEqual(units.TimeUnit('45 sec').raw_value, 45)
        self.assertEqual(units.TimeUnit('45').raw_value, 45)
        self.assertEqual(units.TimeUnit('45.7').raw_value, 45.7)
        self.assertEqual(units.TimeUnit(' 45.7 hour ').raw_value, 45.7*3600)
        self.assertEqual(units.TimeUnit(' 45.7 min ').raw_value, 45.7*60)
        self.assertEqual(units.TimeUnit(' 45.7 day').raw_value, 45.7*(3600*24))
        self.assertEqual(units.TimeUnit(' 45.7 week').raw_value, 45.7*(3600*24*7))
        
        with self.assertRaises(units.ParseError):
            units.TimeUnit('46 dummy')
            
        with self.assertRaises(units.ParseError):
            units.TimeUnit('46.5.6')
            
        with self.assertRaises(units.ParseError):
            units.TimeUnit('46.5.6 ms')
        
    def test_scale(self):
        t = units.TimeUnit(35.54)
        self.assertEqual(t.scale('ms'), 35540)
        self.assertEqual(t.scale('us'), 35540000)
        self.assertEqual(t.scale('ns'), 35540000000)
        self.assertEqual(t.scale('min'), 35.54/60)
        self.assertEqual(t.scale('hour'), 35.54/3600)
        self.assertEqual(t.scale('day'), 35.54/(3600*24))
        self.assertEqual(t.scale('week'), 35.54/(3600*24*7))

    def test_optimal_scale(self):
        self.assertEqual(units.TimeUnit('0 ms').optimal_scale(), (0, 'sec'))
        self.assertEqual(units.TimeUnit('47 ms').optimal_scale(), (47, 'ms'))
        self.assertEqual(units.TimeUnit('4334 ms').optimal_scale(), (4334.0*0.001, 'sec'))
        self.assertEqual(units.TimeUnit('1 hour').optimal_scale(), (1, 'hour'))
        self.assertEqual(units.TimeUnit('1 day').optimal_scale(), (1, 'day'))
        self.assertEqual(units.TimeUnit('1.22 day').optimal_scale(), (1.22, 'day'))
        self.assertEqual(units.TimeUnit('0.96 day').optimal_scale(), (24*0.96, 'hour'))
    
    def test_optimal_combined_scale(self):
        self.assertEqual(units.TimeUnit('0 ms').optimal_combined_scale(),
            [(0, 'sec')])
        self.assertEqual(units.TimeUnit('1.5 ms').optimal_combined_scale(),
            [(1, 'ms'), (500, 'us')])
        self.assertEqual(units.TimeUnit('1 hour').optimal_combined_scale(),
            [(1, 'hour')])
        self.assertEqual(units.TimeUnit('25 hour').optimal_combined_scale(),
            [(1, 'day'),(1, 'hour')])
        self.assertEqual(units.TimeUnit('25.5 hour').optimal_combined_scale(),
            [(1, 'day'),(1, 'hour'), (30, 'min')])
        
    def test_str(self):
        self.assertEqual(str(units.TimeUnit('0 ms')), '0.0 sec')
        self.assertEqual(str(units.TimeUnit('1.2 ms')), '1.2 ms')
        self.assertEqual(str(units.TimeUnit('1500 ms')), '1.5 sec')
        self.assertEqual(str(units.TimeUnit('1.5 day')), '1.5 day')
        self.assertEqual(str(units.TimeUnit('1 day')), '1.0 day')
        
    def test_repr(self):
        self.assertEqual(repr(units.TimeUnit('0 ms')), 'Time(0.0 sec)')
        self.assertEqual(repr(units.TimeUnit('1.2 ms')), 'Time(1.2 ms)')
        self.assertEqual(repr(units.TimeUnit('1500 ms')), 'Time(1.5 sec)')
        self.assertEqual(repr(units.TimeUnit('1.5 day')), 'Time(1.5 day)')
        self.assertEqual(repr(units.TimeUnit('1 day')), 'Time(1.0 day)')

class TestBitRateUnit(unittest.TestCase):
    
    def test_emtpy_constructor(self):
        t = units.BitRateUnit()
        self.assertEqual(t.raw_value, 0)
        
    def test_number_constructor(self):
        t = units.BitRateUnit(1.0)
        self.assertEqual(t.raw_value, 1.0)
        
        t = units.BitRateUnit(3)
        self.assertEqual(t.raw_value, 3.0)
        
        t = units.BitRateUnit(477777.54)
        self.assertEqual(t.raw_value, 477777.54)

    def test_copy_constructor(self):
        
        b1 = units.BitRateUnit(15)
        b2 = units.BitRateUnit(b1)
        self.assertEqual(b1, b2)
        self.assertEqual(b2.raw_value, 15)
        
    def test_parse_constructor(self):
        self.assertEqual(units.BitRateUnit('0').raw_value, 0)
        self.assertEqual(units.BitRateUnit('2.2 bits/s').raw_value, 2.2)
        self.assertEqual(units.BitRateUnit('3.3 bit/s').raw_value, 3.3)
        self.assertEqual(units.BitRateUnit('4.4 bps').raw_value, 4.4)
        self.assertEqual(units.BitRateUnit('1.4 Gbit/s').raw_value, 1.4*(10**9))
        self.assertEqual(units.BitRateUnit('1.5 Gbits/s').raw_value, 1.5*(10**9))
        self.assertEqual(units.BitRateUnit('1.6 Gbps').raw_value, 1.6*(10**9))
        self.assertEqual(units.BitRateUnit('1.4 Mbit/s').raw_value, 1.4*(10**6))
        self.assertEqual(units.BitRateUnit('1.5 Mbits/s').raw_value, 1.5*(10**6))
        self.assertEqual(units.BitRateUnit('1.6 Mbps').raw_value, 1.6*(10**6))
        self.assertEqual(units.BitRateUnit('1.4 Kbit/s').raw_value, 1.4*(10**3))
        self.assertEqual(units.BitRateUnit('1.5 Kbits/s').raw_value, 1.5*(10**3))
        self.assertEqual(units.BitRateUnit('1.6 Kbps').raw_value, 1.6*(10**3))
        self.assertEqual(units.BitRateUnit('1.4 Tbit/s').raw_value, 1.4*(10**12))
        self.assertEqual(units.BitRateUnit('1.5 Tbits/s').raw_value, 1.5*(10**12))
        self.assertEqual(units.BitRateUnit('1.6 Tbps').raw_value, 1.6*(10**12))
        
        with self.assertRaises(units.ParseError):
            units.BitRateUnit('46 dummy')
            
        with self.assertRaises(units.ParseError):
            units.BitRateUnit('46.5.6')
            
        with self.assertRaises(units.ParseError):
            units.BitRateUnit('46.5.6 kb ps')
        
    def test_scale(self):
        t = units.BitRateUnit(356500000)
        self.assertEqual(t.scale('Kbps'), 356500)
        self.assertEqual(t.scale('kbit/s'), 356500)
        self.assertEqual(t.scale('Mbit/s'), 356.5)
        self.assertEqual(t.scale('Mbits/s'), 356.5)
        self.assertEqual(t.scale('Mbps'), 356.5)
        self.assertEqual(t.scale('Gbit/s'), 0.3565)
        self.assertEqual(t.scale('Gbits/s'), 0.3565)
        self.assertEqual(t.scale('Gbps'), 0.3565)
        self.assertEqual(t.scale('Tbit/s'), 0.0003565)
        self.assertEqual(t.scale('Tbits/s'), 0.0003565)
        self.assertEqual(t.scale('Tbps'), 0.0003565)

    def test_optimal_scale(self):
        self.assertEqual(units.BitRateUnit('0 bps').optimal_scale(), (0, 'bits/s'))
        self.assertEqual(units.BitRateUnit('100 bps').optimal_scale(), (100, 'bits/s'))
        self.assertEqual(units.BitRateUnit('1000 bps').optimal_scale(), (1, 'kbit/s'))
        self.assertEqual(units.BitRateUnit('1100 bps').optimal_scale(), (1.1, 'kbit/s'))
        self.assertEqual(units.BitRateUnit('0.00054 bps').optimal_scale(), (0.00054, 'bits/s'))
        self.assertEqual(units.BitRateUnit('1 Gbit/s').optimal_scale(), (1, 'Gbit/s'))
        self.assertEqual(units.BitRateUnit('1 Tbit/s').optimal_scale(), (1, 'Tbit/s'))

        
    def test_str(self):
        self.assertEqual(str(units.BitRateUnit('1 Gbps')), '1.0 Gbit/s')
        self.assertEqual(str(units.BitRateUnit('1.2 kbit/s')), '1.2 kbit/s')
        self.assertEqual(str(units.BitRateUnit('400 Tbps')), '400.0 Tbit/s')

        
    def test_repr(self):
        self.assertEqual(repr(units.BitRateUnit('1.1 Gbps')), 'Transfer Rate(1.1 Gbit/s)')
        self.assertEqual(repr(units.BitRateUnit('1.2 kbit/s')), 'Transfer Rate(1.2 kbit/s)')
        self.assertEqual(repr(units.BitRateUnit('400 Tbps')), 'Transfer Rate(400.0 Tbit/s)')

class TestMagicFunctions(unittest.TestCase):
    
    
    def test_nonzero(self):
    
        self.assertFalse(units.BitRateUnit(0))
        self.assertTrue(units.BitRateUnit(1))
    
    def test_cmp(self):
        self.assertFalse(units.BitRateUnit(1) == units.BitRateUnit(0))
        self.assertTrue(units.BitRateUnit(1) != units.BitRateUnit(0))
        self.assertFalse(units.BitRateUnit(1) < units.BitRateUnit(0))
        self.assertFalse(units.BitRateUnit(1) <= units.BitRateUnit(0))
        self.assertTrue(units.BitRateUnit(1) > units.BitRateUnit(0))
        self.assertTrue(units.BitRateUnit(1) >= units.BitRateUnit(0))
        
        self.assertTrue(units.BitRateUnit(1) == units.BitRateUnit(1))
        self.assertFalse(units.BitRateUnit(1) != units.BitRateUnit(1))
        self.assertFalse(units.BitRateUnit(1) < units.BitRateUnit(1))
        self.assertTrue(units.BitRateUnit(1) <= units.BitRateUnit(1))
        self.assertFalse(units.BitRateUnit(1) > units.BitRateUnit(1))
        self.assertTrue(units.BitRateUnit(1) >= units.BitRateUnit(1))
        
        self.assertFalse(units.BitRateUnit(0) == units.BitRateUnit(1))
        self.assertTrue(units.BitRateUnit(0) != units.BitRateUnit(1))
        self.assertTrue(units.BitRateUnit(0) < units.BitRateUnit(1))
        self.assertTrue(units.BitRateUnit(0) <= units.BitRateUnit(1))
        self.assertFalse(units.BitRateUnit(0) > units.BitRateUnit(1))
        self.assertFalse(units.BitRateUnit(0) >= units.BitRateUnit(1))

    def test_add(self):
        a = units.BitRateUnit(4.5)
        b = units.BitRateUnit(1.2)
        self.assertEqual(a + b, units.BitRateUnit(5.7))

    def test_sub(self):
        a = units.BitRateUnit(4.5)
        b = units.BitRateUnit(1.2)
        self.assertEqual(a - b, units.BitRateUnit(3.3))


class TestPersentage(unittest.TestCase):
    
    def test_constructor(self):
        self.assertEqual(units.PercentageUnit('1').raw_value, 1)
        self.assertEqual(units.PercentageUnit('10%').raw_value, 10)
        self.assertEqual(units.PercentageUnit('30.2 %').raw_value, 30.2)
        
    def test_str(self):
        self.assertEqual(str(units.PercentageUnit('1')), '1.0 %')
        self.assertEqual(str(units.PercentageUnit('110')), '110.0 %')
        
class TestByteRate(unittest.TestCase):
    
    def test_constructor(self):
        self.assertEqual(units.ByteRateUnit('1').raw_value, 1)
        self.assertEqual(units.ByteRateUnit('10 Bps').raw_value, 10)
        self.assertEqual(units.ByteRateUnit('10 kBps').raw_value, 10000)
        self.assertEqual(units.ByteRateUnit('10 KBps').raw_value, 10000)
        self.assertEqual(units.ByteRateUnit('10 KByte/s').raw_value, 10000)
        self.assertEqual(units.ByteRateUnit('10 MBps').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRateUnit('10 MBytes/s').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRateUnit('10 MByte/s').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRateUnit('10 GBps').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRateUnit('10 GBytes/s').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRateUnit('10 GByte/s').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRateUnit('10 TBps').raw_value, 10*(10**12))
        self.assertEqual(units.ByteRateUnit('10 TBytes/s').raw_value, 10*(10**12))
        self.assertEqual(units.ByteRateUnit('10 TByte/s').raw_value, 10*(10**12))
        
