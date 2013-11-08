'''
Created on Nov 5, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

import re

class ParseError(RuntimeError):
    '''
    Error when parsing a unit
    '''

class Unit(object):
    '''
    Base class for defining a measurement unit
    '''
    def __init__(self, name, initial_value, magnitudes, alt_magnitude_names = {}):
        '''
        @param name A friendly name describing the unit
        @param initial_vale The initial value of this object
        @param mangitudes A list of tuples with names and orders of magnitudes
        @param alt_magnitude_names A dictionary of list with alternative names per magnitude
        '''

        self.name = name
        self.raw_value = initial_value
        self.magnitudes = magnitudes
        self.alt_magnitude_names = alt_magnitude_names
        self.magnitudes_map = {}
        self.default_magnitude = None
        
        # Initialize values
        for magnitude in self.magnitudes:
            self.magnitudes_map[magnitude[1]] = float(magnitude[0])
            if magnitude[0] == 1:
                self.default_magnitude = magnitude[1]
        
        if self.default_magnitude is None:
            raise LookupError("A magnitude of order 1 is mandatory.")
        
    
    def scale(self, magnitude):
        '''
        Scale value to a different magnitude
        '''
        if magnitude not in self.magnitudes_map.keys():
            raise LookupError("Unknown magnitude '{0}'".format(magnitude))
        
        return float(self.raw_value) / self.magnitudes_map[magnitude]

    def optimal_scale(self):
        '''
        It will return the magnitude that is
        closer and above 1. The return value is a tuple
        containing the value and the magnitude.
        ''' 
        
        # If zero Return unscaled to default magnitude 
        if self.raw_value == 0:
            return (self.raw_value, self.default_magnitude) 
        
        
        # Try to increment one order each time
        best_magnitude = self.default_magnitude
        for magnitude in reversed(self.magnitudes):
            if self.scale(magnitude[1]) > 1:
                best_magnitude = magnitude[1]
                break;
        
        # Return best one
        return (self.scale(best_magnitude), best_magnitude)
    
    def optimal_combined_scale(self):
        '''
        It will divide value in a sum of multiple
        integral scales instead of one floating point.
        The result is a list of tuples with value and magnitude
        '''
        
        # If zero Return unscaled to default magnitude 
        if self.raw_value == 0:
            return [(self.raw_value, self.default_magnitude)]
        
        scales = []
        value = float(self.raw_value)
        for magnitude in reversed(self.magnitudes):
            div = divmod(value, magnitude[0])
            if div[0] >= 1:
                scales.append((int(div[0]), magnitude[1]))
                value = div[1]
                if value < 10**-10: # Tune this to drop floating round problems
                    break
        if not scales:
            scales.append((value, self.magnitudes[0][1]))
        return scales
    
    def parse(self, string):
        '''
        Check objects value by parsing a string formatted expression
        ''' 
        pattern = re.compile('^\s*([0-9\.]+)\s*([^\s]+)\s*$')
        match = pattern.match(string)
        if not match:
            raise ParseError("Error parsing '{0}'".format(string))
        
        quantity = float(match.group(1))
        unit_type = match.group(2)
        for magnitude,order in self.magnitudes_map.iteritems():
            if unit_type == magnitude or unit_type in self.alt_magnitude_names[magnitude]:
                self.raw_value = order * quantity
                return # Found
                
        
        raise ParseError("Error parsing '{0}'".format(string))

    def optimal_scale_str(self):
        '''
        Return the optimal scale in a string format
        '''
        optimal_scale = self.optimal_scale()
        return "{0} {1}".format(optimal_scale[0], optimal_scale[1])
    
    def optimal_combined_scale_str(self):
        '''
        Return the optimal scale in a string format
        '''
        chunks = []
        for magnitude in self.optimal_combined_scale():
            chunks.append("{0} {1}".format(magnitude[0], magnitude[1]))
        return " ".join(chunks)
    
    def __str__(self):
        return self.optimal_scale_str()
    
    def __repr__(self):
        return "{0}({1})".format(self.name, self.__str__())
    
    def __eq__(self, other):
        assert type(self) == type(other)
        return self.raw_value == other.raw_value

    def __ne__(self, other):
        assert type(self) == type(other)
        return self.raw_value != other.raw_value
    
    def __lt__(self, other):
        assert type(self) == type(other)
        return self.raw_value < other.raw_value
    
    def __le__(self, other):
        assert type(self) == type(other)
        return self.raw_value <= other.raw_value
    
    def __gt__(self, other):
        assert type(self) == type(other)
        return self.raw_value > other.raw_value
    
    def __ge__(self, other):
        assert type(self) == type(other)
        return self.raw_value >= other.raw_value
    
    def __nonzero__(self):
        return bool(self.raw_value)
    
    def __add__(self, other):
        assert type(self) == type(other)
        return type(self)(self.raw_value + other.raw_value)
    
    def __sub__(self, other):
        assert type(self) == type(other)
        return type(self)(self.raw_value - other.raw_value)
    
class BitRateUnit(Unit):
    '''
    BitRate measurement unit
    '''
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1,     'bits/s'),
                      (10**3, 'kbit/s'),
                      (10**6, 'Mbit/s'),
                      (10**9, 'Gbit/s'),
                      (10**11,'Tbit/s')]
        
        alt_magnitude_names = {
                'bits/s' : ['b/s', 'bps'],
                'kbit/s' : ['Kbit/s', 'Kbits/s', 'Kb/s', 'kbps'],
                'Mbit/s' : ['Mbits/s', 'Mb/s', 'Mbps'],
                'Gbit/s' : ['Gbits/s', 'Gb/s', 'Gbps'],
                'Tbit/s' : ['Tbits/s', 'Tb/s', 'Tbps'],
                }
        
        super(BitRateUnit, self).__init__("Transfer Rate", initial_value, magnitudes, alt_magnitude_names)

class ByteRateUnit(Unit):
    '''
    ByteRate measurement unit
    '''
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1,     'bytes/s'),
                      (10**3, 'KByte/s'),
                      (10**6, 'MByte/s'),
                      (10**9, 'GByte/s'),
                      (10**11,'TByte/s')]
        
        alt_magnitude_names = {
                'bytes/s' : ['Bytes/s', 'B/s', 'Bps'],
                'KByte/s' : ['KByte/s', 'KBytes/s', 'KB/s', 'kBps'],
                'MByte/s' : ['MBytes/s', 'MB/s', 'MBps'],
                'GByte/s' : ['GBytes/s', 'GB/s', 'GBps'],
                'TByte/s' : ['TBytes/s', 'TB/s', 'TBps'],
                }
        
        super(ByteRateUnit, self).__init__("Transfer Rate", initial_value, magnitudes, alt_magnitude_names)


class TimeUnit(Unit):
    '''
    Time measurement unit (seconds)
    '''
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (10**(-9), 'ns'),
                      (10**(-6), 'us'),
                      (10**(-3), 'ms'),
                      (1,        'sec'),
                      (60,       'min'),
                      (3600,     'hour'),
                      (3600*24,  'day'),
                      ]
        super(TimeUnit, self).__init__("Time", initial_value, magnitudes)

class PercentageUnit(Unit):
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1 , '%')
                     ]
        super(PercentageUnit, self).__init__("Percentage", initial_value, magnitudes)

class PacketUnit(Unit):
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1 , 'p')
                     ]
        super(PacketUnit, self).__init__("Packets", initial_value, magnitudes)

# Example usage
if __name__ == '__main__':
    times = [TimeUnit(),
             TimeUnit(0),
             TimeUnit(65),
             TimeUnit(1553.43),
             TimeUnit(3660.5),
             TimeUnit(0.020),
             TimeUnit(0.0001)
             ]
    print "Optimal Scale"
    # Time
    for time in times:
        print "Time| raw: {0}, optimal : {1}, combined: {2}, str: '{3}'".format(
                    time.raw_value,
                    time.optimal_scale(),
                    time.optimal_combined_scale(),
                    str(time))
    
    rates = [BitRateUnit(),
             BitRateUnit(0),
             BitRateUnit(1000),
             BitRateUnit(1024),
             BitRateUnit(2000000)
             ]
    # Time
    for rate in rates:
        print "Rates| raw: {0}, optimal : {1}, combined: {2}, str: '{3}'".format(
                    rate.raw_value,
                    rate.optimal_scale(),
                    rate.optimal_combined_scale(),
                    str(rate))

    # Percentage
    print PercentageUnit()
    print PercentageUnit(90)
    print PercentageUnit(11.1)
    
    print PacketUnit()
    print PacketUnit(12)
    print PacketUnit(14)
    
    print "UNIT TESTING"
    print "------------------------------------------"
    print "Parsing"
    bit_tests = [
                ("1bps", BitRateUnit(1)),
                ("40 bps", BitRateUnit(40)),
                ("47 bits/s", BitRateUnit(47)),
                ("12.67 Gbits/s", BitRateUnit(12.67*1000*1000*1000)),
                ("12.32 Gb/s", BitRateUnit(12.32*1000*1000*1000)),
                ("12.543 Gbps", BitRateUnit(12.543*1000*1000*1000))
            ]
    
    for btest in bit_tests:
        b = BitRateUnit()
        b.parse(btest[0])
        assert b == btest[1]
        print btest[0], b, btest[1] 
    
    try:
        b.parse("12.543 dummy")
    except:
        print "Caught exception as expected"
        
    
    byte_tests = [
                ("1Bps", ByteRateUnit(1)),
                ("40 Bps", ByteRateUnit(40)),
                ("47 Bytes/s", ByteRateUnit(47)),
                ("12.67 GBytes/s", ByteRateUnit(12.67*1000*1000*1000)),
                ("12.32 GB/s", ByteRateUnit(12.32*1000*1000*1000)),
                ("12.543 GBps", ByteRateUnit(12.543*1000*1000*1000))
            ]
    
    for btest in byte_tests:
        b = ByteRateUnit()
        b.parse(btest[0])
        assert b == btest[1]
        print btest[0], b, btest[1] 
    
    try:
        b.parse("12.543 dummy")
    except:
        print "Caught exception as expected"
        
        
    print "\nComparisons"
    assert not BitRateUnit(0)
    assert BitRateUnit(1)
    
    assert not BitRateUnit(1) == BitRateUnit(0)
    assert BitRateUnit(1) != BitRateUnit(0)
    assert not BitRateUnit(1) < BitRateUnit(0)
    assert not BitRateUnit(1) <= BitRateUnit(0)
    assert BitRateUnit(1) > BitRateUnit(0)
    assert BitRateUnit(1) >= BitRateUnit(0)
    
    assert BitRateUnit(1) == BitRateUnit(1)
    assert not BitRateUnit(1) != BitRateUnit(1)
    assert not BitRateUnit(1) < BitRateUnit(1)
    assert BitRateUnit(1) <= BitRateUnit(1)
    assert not BitRateUnit(1) > BitRateUnit(1)
    assert BitRateUnit(1) >= BitRateUnit(1)
    
    assert not BitRateUnit(0) == BitRateUnit(1)
    assert BitRateUnit(0) != BitRateUnit(1)
    assert BitRateUnit(0) < BitRateUnit(1)
    assert BitRateUnit(0) <= BitRateUnit(1)
    assert not BitRateUnit(0) > BitRateUnit(1)
    assert not BitRateUnit(0) >= BitRateUnit(1)
    print "Passed."

    print "\nArithmetic operations"
    a = BitRateUnit(4.5)
    b = BitRateUnit(1.2)
    c = BitRateUnit(5.7)
    print "a + b = c => {0} + {1} = {2}".format(a, b, a+b)
    assert a+b == c
    c = BitRateUnit(3.3)
    print "a - b = c => {0} - {1} = {2}".format(a, b, a-c)
    assert a-b == c