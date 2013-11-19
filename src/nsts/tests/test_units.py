
from __future__ import absolute_import
import unittest
from nsts import units

class TestTimeUnit(unittest.TestCase):
    
    def test_emtpy_constructor(self):
        t = units.Time()
        self.assertEqual(t.raw_value, 0)
        
    def test_number_constructor(self):
        t = units.Time(1.0)
        self.assertEqual(t.raw_value, 1.0)
        
        t = units.Time(3)
        self.assertEqual(t.raw_value, 3.0)
        
        t = units.Time(477777.54)
        self.assertEqual(t.raw_value, 477777.54)

    def test_copy_constructor(self):
        
        t1 = units.Time(15)
        t2 = units.Time(t1)
        self.assertEqual(t1, t2)
        self.assertEqual(t2.raw_value, 15)
        
    def test_parse_constructor(self):
        self.assertEqual(units.Time('0 ms').raw_value, 0)
        self.assertEqual(units.Time('1 ms').raw_value, 0.001)
        self.assertEqual(units.Time('1.5 ms').raw_value, 0.0015)
        self.assertEqual(units.Time('45 sec').raw_value, 45)
        self.assertEqual(units.Time('45').raw_value, 45)
        self.assertEqual(units.Time('45.7').raw_value, 45.7)
        self.assertEqual(units.Time(' 45.7 hour ').raw_value, 45.7*3600)
        self.assertEqual(units.Time(' 45.7 min ').raw_value, 45.7*60)
        self.assertEqual(units.Time(' 45.7 day').raw_value, 45.7*(3600*24))
        self.assertEqual(units.Time(' 45.7 week').raw_value, 45.7*(3600*24*7))
        
        with self.assertRaises(units.ParseError):
            units.Time('46 dummy')
            
        with self.assertRaises(units.ParseError):
            units.Time('46.5.6')
            
        with self.assertRaises(units.ParseError):
            units.Time('46.5.6 ms')
        
    def test_scale(self):
        t = units.Time(35.54)
        self.assertEqual(t.scale('ms'), 35540)
        self.assertEqual(t.scale('us'), 35540000)
        self.assertEqual(t.scale('ns'), 35540000000)
        self.assertEqual(t.scale('min'), 35.54/60)
        self.assertEqual(t.scale('hour'), 35.54/3600)
        self.assertEqual(t.scale('day'), 35.54/(3600*24))
        self.assertEqual(t.scale('week'), 35.54/(3600*24*7))

    def test_optimal_scale(self):
        self.assertEqual(units.Time('0 ms').optimal_scale(), (0, 'sec'))
        self.assertEqual(units.Time('47 ms').optimal_scale(), (47, 'ms'))
        self.assertEqual(units.Time('4334 ms').optimal_scale(), (4334.0*0.001, 'sec'))
        self.assertEqual(units.Time('1 hour').optimal_scale(), (1, 'hour'))
        self.assertEqual(units.Time('1 day').optimal_scale(), (1, 'day'))
        self.assertEqual(units.Time('1.22 day').optimal_scale(), (1.22, 'day'))
        self.assertEqual(units.Time('0.96 day').optimal_scale(), (24*0.96, 'hour'))
    
    def test_optimal_combined_scale(self):
        self.assertEqual(units.Time('0 ms').optimal_combined_scale(),
            [(0, 'sec')])
        self.assertEqual(units.Time('1.5 ms').optimal_combined_scale(),
            [(1, 'ms'), (500, 'us')])
        self.assertEqual(units.Time('1 hour').optimal_combined_scale(),
            [(1, 'hour')])
        self.assertEqual(units.Time('25 hour').optimal_combined_scale(),
            [(1, 'day'),(1, 'hour')])
        self.assertEqual(units.Time('25.5 hour').optimal_combined_scale(),
            [(1, 'day'),(1, 'hour'), (30, 'min')])
        
    def test_str(self):
        self.assertEqual(str(units.Time('0 ms')), '0.0 sec')
        self.assertEqual(str(units.Time('1.2 ms')), '1.2 ms')
        self.assertEqual(str(units.Time('1500 ms')), '1.5 sec')
        self.assertEqual(str(units.Time('1.5 day')), '1.5 day')
        self.assertEqual(str(units.Time('1 day')), '1.0 day')
        
    def test_repr(self):
        self.assertEqual(repr(units.Time('0 ms')), 'Time(0.0 sec)')
        self.assertEqual(repr(units.Time('1.2 ms')), 'Time(1.2 ms)')
        self.assertEqual(repr(units.Time('1500 ms')), 'Time(1.5 sec)')
        self.assertEqual(repr(units.Time('1.5 day')), 'Time(1.5 day)')
        self.assertEqual(repr(units.Time('1 day')), 'Time(1.0 day)')

class TestBitRateUnit(unittest.TestCase):
    
    def test_emtpy_constructor(self):
        t = units.BitRate()
        self.assertEqual(t.raw_value, 0)
        
    def test_number_constructor(self):
        t = units.BitRate(1.0)
        self.assertEqual(t.raw_value, 1.0)
        
        t = units.BitRate(3)
        self.assertEqual(t.raw_value, 3.0)
        
        t = units.BitRate(477777.54)
        self.assertEqual(t.raw_value, 477777.54)

    def test_copy_constructor(self):
        
        b1 = units.BitRate(15)
        b2 = units.BitRate(b1)
        self.assertEqual(b1, b2)
        self.assertEqual(b2.raw_value, 15)
        
    def test_parse_constructor(self):
        self.assertEqual(units.BitRate('0').raw_value, 0)
        self.assertEqual(units.BitRate('2.2 bits/s').raw_value, 2.2)
        self.assertEqual(units.BitRate('3.3 bit/s').raw_value, 3.3)
        self.assertEqual(units.BitRate('4.4 bps').raw_value, 4.4)
        self.assertEqual(units.BitRate('1.4 Gbit/s').raw_value, 1.4*(10**9))
        self.assertEqual(units.BitRate('1.5 Gbits/s').raw_value, 1.5*(10**9))
        self.assertEqual(units.BitRate('1.6 Gbps').raw_value, 1.6*(10**9))
        self.assertEqual(units.BitRate('1.4 Mbit/s').raw_value, 1.4*(10**6))
        self.assertEqual(units.BitRate('1.5 Mbits/s').raw_value, 1.5*(10**6))
        self.assertEqual(units.BitRate('1.6 Mbps').raw_value, 1.6*(10**6))
        self.assertEqual(units.BitRate('1.4 Kbit/s').raw_value, 1.4*(10**3))
        self.assertEqual(units.BitRate('1.5 Kbits/s').raw_value, 1.5*(10**3))
        self.assertEqual(units.BitRate('1.6 Kbps').raw_value, 1.6*(10**3))
        self.assertEqual(units.BitRate('1.4 Tbit/s').raw_value, 1.4*(10**12))
        self.assertEqual(units.BitRate('1.5 Tbits/s').raw_value, 1.5*(10**12))
        self.assertEqual(units.BitRate('1.6 Tbps').raw_value, 1.6*(10**12))
        
        with self.assertRaises(units.ParseError):
            units.BitRate('46 dummy')
            
        with self.assertRaises(units.ParseError):
            units.BitRate('46.5.6')
            
        with self.assertRaises(units.ParseError):
            units.BitRate('46.5.6 kb ps')
        
    def test_scale(self):
        t = units.BitRate(356500000)
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
        self.assertEqual(units.BitRate('0 bps').optimal_scale(), (0, 'bits/s'))
        self.assertEqual(units.BitRate('100 bps').optimal_scale(), (100, 'bits/s'))
        self.assertEqual(units.BitRate('1000 bps').optimal_scale(), (1, 'kbit/s'))
        self.assertEqual(units.BitRate('1100 bps').optimal_scale(), (1.1, 'kbit/s'))
        self.assertEqual(units.BitRate('0.00054 bps').optimal_scale(), (0.00054, 'bits/s'))
        self.assertEqual(units.BitRate('1 Gbit/s').optimal_scale(), (1, 'Gbit/s'))
        self.assertEqual(units.BitRate('1 Tbit/s').optimal_scale(), (1, 'Tbit/s'))

        
    def test_str(self):
        self.assertEqual(str(units.BitRate('1 Gbps')), '1.0 Gbit/s')
        self.assertEqual(str(units.BitRate('1.2 kbit/s')), '1.2 kbit/s')
        self.assertEqual(str(units.BitRate('400 Tbps')), '400.0 Tbit/s')

        
    def test_repr(self):
        self.assertEqual(repr(units.BitRate('1.1 Gbps')), 'Transfer Rate(1.1 Gbit/s)')
        self.assertEqual(repr(units.BitRate('1.2 kbit/s')), 'Transfer Rate(1.2 kbit/s)')
        self.assertEqual(repr(units.BitRate('400 Tbps')), 'Transfer Rate(400.0 Tbit/s)')

class TestMagicFunctions(unittest.TestCase):
    
    
    def test_nonzero(self):
    
        self.assertFalse(units.BitRate(0))
        self.assertTrue(units.BitRate(1))
    
    def test_cmp(self):
        self.assertFalse(units.BitRate(1) == units.BitRate(0))
        self.assertTrue(units.BitRate(1) != units.BitRate(0))
        self.assertFalse(units.BitRate(1) < units.BitRate(0))
        self.assertFalse(units.BitRate(1) <= units.BitRate(0))
        self.assertTrue(units.BitRate(1) > units.BitRate(0))
        self.assertTrue(units.BitRate(1) >= units.BitRate(0))
        
        self.assertTrue(units.BitRate(1) == units.BitRate(1))
        self.assertFalse(units.BitRate(1) != units.BitRate(1))
        self.assertFalse(units.BitRate(1) < units.BitRate(1))
        self.assertTrue(units.BitRate(1) <= units.BitRate(1))
        self.assertFalse(units.BitRate(1) > units.BitRate(1))
        self.assertTrue(units.BitRate(1) >= units.BitRate(1))
        
        self.assertFalse(units.BitRate(0) == units.BitRate(1))
        self.assertTrue(units.BitRate(0) != units.BitRate(1))
        self.assertTrue(units.BitRate(0) < units.BitRate(1))
        self.assertTrue(units.BitRate(0) <= units.BitRate(1))
        self.assertFalse(units.BitRate(0) > units.BitRate(1))
        self.assertFalse(units.BitRate(0) >= units.BitRate(1))

    def test_add(self):
        a = units.BitRate(4.5)
        b = units.BitRate(1.2)
        self.assertEqual(a + b, units.BitRate(5.7))

    def test_sub(self):
        a = units.BitRate(4.5)
        b = units.BitRate(1.2)
        self.assertEqual(a - b, units.BitRate(3.3))


class TestPersentage(unittest.TestCase):
    
    def test_constructor(self):
        self.assertEqual(units.Percentage('1').raw_value, 1)
        self.assertEqual(units.Percentage('10%').raw_value, 10)
        self.assertEqual(units.Percentage('30.2 %').raw_value, 30.2)
        
    def test_str(self):
        self.assertEqual(str(units.Percentage('1')), '1.0 %')
        self.assertEqual(str(units.Percentage('110')), '110.0 %')
        
class TestByteRate(unittest.TestCase):
    
    def test_constructor(self):
        self.assertEqual(units.ByteRate('1').raw_value, 1)
        self.assertEqual(units.ByteRate('10 Bps').raw_value, 10)
        self.assertEqual(units.ByteRate('10 kBps').raw_value, 10000)
        self.assertEqual(units.ByteRate('10 KBps').raw_value, 10000)
        self.assertEqual(units.ByteRate('10 KByte/s').raw_value, 10000)
        self.assertEqual(units.ByteRate('10 MBps').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRate('10 MBytes/s').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRate('10 MByte/s').raw_value, 10*(10**6))
        self.assertEqual(units.ByteRate('10 GBps').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRate('10 GBytes/s').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRate('10 GByte/s').raw_value, 10*(10**9))
        self.assertEqual(units.ByteRate('10 TBps').raw_value, 10*(10**12))
        self.assertEqual(units.ByteRate('10 TBytes/s').raw_value, 10*(10**12))
        self.assertEqual(units.ByteRate('10 TByte/s').raw_value, 10*(10**12))

class TestByte(unittest.TestCase):
    
    def test_constructor(self):
        self.assertEqual(units.Byte('1').raw_value, 1)
        self.assertEqual(units.Byte('10 B').raw_value, 10)
        self.assertEqual(units.Byte('10 KBytes').raw_value, 10000)
        self.assertEqual(units.Byte('10 Kbyte').raw_value, 10000)
        self.assertEqual(units.Byte('10 kbyte').raw_value, 10000)
        self.assertEqual(units.Byte('10 KB').raw_value, 10000)
        self.assertEqual(units.Byte('10 KByte').raw_value, 10000)
        self.assertEqual(units.Byte('10 MB').raw_value, 10*(10**6))
        self.assertEqual(units.Byte('10 MBytes').raw_value, 10*(10**6))
        self.assertEqual(units.Byte('10 MByte').raw_value, 10*(10**6))
        self.assertEqual(units.Byte('10 Mbyte').raw_value, 10*(10**6))
        self.assertEqual(units.Byte('10 GB').raw_value, 10*(10**9))
        self.assertEqual(units.Byte('10 GBytes').raw_value, 10*(10**9))
        self.assertEqual(units.Byte('10 GByte').raw_value, 10*(10**9))
        self.assertEqual(units.Byte('10 Gbyte').raw_value, 10*(10**9))
        self.assertEqual(units.Byte('10 TB').raw_value, 10*(10**12))
        self.assertEqual(units.Byte('10 TBytes').raw_value, 10*(10**12))
        self.assertEqual(units.Byte('10 TByte').raw_value, 10*(10**12))
        self.assertEqual(units.Byte('10 Tbyte').raw_value, 10*(10**12))

