'''
Module for manipulating different type of units. It supports
parsing and rendering to and from human readable representations.

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''

import re

class ParseError(RuntimeError):
    '''
    Error when parsing a unit
    '''

class UnknownMangitudeError(ParseError):
    '''
    Error raised when an unknown magnitude was requested
    '''
    def __init__(self, magnitude, unit):
        super(UnknownMangitudeError, self).__init__(
                "Unknown magnitude '{0}' for unit '{1}'"
                .format(magnitude, unit.name))

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
        
        # Check if parsing is needed
        if isinstance(initial_value, basestring):
            self.__parse(initial_value)
        # Check if it is a copy constructor
        elif type(self) == type(initial_value):
            self.raw_value = initial_value.raw_value
        else:
            self.raw_value = float(initial_value)

    def __magnitude_order(self, magn_search):
        '''
        Get the magnitude order based on name
        '''
        for magnitude,order in self.magnitudes_map.iteritems():
            if magn_search == magnitude \
                or (self.alt_magnitude_names.has_key(magnitude) 
                    and magn_search in self.alt_magnitude_names[magnitude]):
                return order
        raise UnknownMangitudeError(magn_search, self)
    
    def __parse(self, string):
        '''
        Check objects value by parsing a string formatted expression
        ''' 
        pattern = re.compile('^\s*(\d+(?:\.\d*)?)\s*([^\s]*)\s*$')
        match = pattern.match(string)
        if not match:
            raise ParseError("Cannot parse '{0}' as {1} unit.".format(
                    string,
                    self.name))
        
        quantity = float(match.group(1))
        unit_type = match.group(2)
        if not unit_type:
            unit_type = self.default_magnitude

        self.raw_value = self.__magnitude_order(unit_type) * quantity
        
        
    def scale(self, magnitude):
        '''
        Scale value to a different magnitude
        '''
        return float(self.raw_value) / self.__magnitude_order(magnitude)

    def optimal_scale(self):
        '''
        Calculate the magnitude that is closer and
        above 1. The return value is a tuple
        containing the value and the magnitude.
        ''' 
        
        # If zero Return unscaled to default magnitude 
        if self.raw_value == 0:
            return (self.raw_value, self.default_magnitude) 
        
        
        # Try to increment one order each time
        best_magnitude = self.default_magnitude
        for magnitude in reversed(self.magnitudes):
            if self.scale(magnitude[1]) >= 1:
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
    
class BitRate(Unit):
    '''
    BitRate measurement unit
    '''
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1,     'bits/s'),
                      (10**3, 'kbit/s'),
                      (10**6, 'Mbit/s'),
                      (10**9, 'Gbit/s'),
                      (10**12,'Tbit/s')]
        
        alt_magnitude_names = {
                'bits/s' : ['bit/s', 'b/s', 'bps'],
                'kbit/s' : ['Kbit/s', 'Kbits/s', 'Kb/s', 'Kbps'],
                'Mbit/s' : ['Mbits/s', 'Mb/s', 'Mbps'],
                'Gbit/s' : ['Gbits/s', 'Gb/s', 'Gbps'],
                'Tbit/s' : ['Tbits/s', 'Tb/s', 'Tbps'],
                }
        
        super(BitRate, self).__init__("Transfer Rate", initial_value, magnitudes, alt_magnitude_names)

class ByteRate(Unit):
    '''
    ByteRate measurement unit
    '''
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1,     'bytes/s'),
                      (10**3, 'KByte/s'),
                      (10**6, 'MByte/s'),
                      (10**9, 'GByte/s'),
                      (10**12,'TByte/s')]
        
        alt_magnitude_names = {
                'bytes/s' : ['Bytes/s', 'B/s', 'Bps'],
                'KByte/s' : ['KByte/s', 'KBytes/s', 'KB/s', 'kBps', 'KBps'],
                'MByte/s' : ['MBytes/s', 'MB/s', 'MBps'],
                'GByte/s' : ['GBytes/s', 'GB/s', 'GBps'],
                'TByte/s' : ['TBytes/s', 'TB/s', 'TBps'],
                }
        
        super(ByteRate, self).__init__("Transfer Rate", initial_value, magnitudes, alt_magnitude_names)


class Time(Unit):
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
                      (3600*24*7,'week'),
                      ]
        super(Time, self).__init__("Time", initial_value, magnitudes)

class Percentage(Unit):
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1 , '%')
                     ]
        super(Percentage, self).__init__("Percentage", initial_value, magnitudes)

class Packet(Unit):
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1 , 'p')
                     ]
        super(Packet, self).__init__("Packets", initial_value, magnitudes)

class Byte(Unit):
    '''
    Byte measurement unit
    '''
    
    def __init__(self, initial_value = 0):
        magnitudes = [
                      (1,     'bytes'),
                      (10**3, 'KBytes'),
                      (10**6, 'MBytes'),
                      (10**9, 'GBytes'),
                      (10**12,'TBytes')]
        
        alt_magnitude_names = {
                'bytes' : ['Byte', 'B'],
                'KBytes' : ['KByte', 'Kbyte', 'kbyte', 'KB'],
                'MBytes' : ['MByte', 'Mbyte', 'MB'],
                'GBytes' : ['GByte', 'Gbyte', 'GB'],
                'TBytes' : ['TByte', 'Tbyte', 'TB'],
                }
        
        super(Byte, self).__init__('Information Quantity', initial_value, magnitudes, alt_magnitude_names)
