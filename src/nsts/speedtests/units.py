'''
Created on Nov 5, 2013

@author: Konstantinos Paliouras <sque '' tolabaki '' gr>
'''

class Unit(object):
    '''
    Base class for defining a measurement unit
    '''
    def __init__(self, name, initial_value, magnitudes):
        
        self.name = name
        self.raw_value = initial_value
        self.magnitudes = magnitudes
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
        super(BitRateUnit, self).__init__("Transfer Rate", initial_value, magnitudes)
 

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

    def __str__(self):
        return self.optimal_combined_scale_str()

class PercentageUnit(Unit):
    
    def __init__(self, initial_value = 0):
        magnitudes = [1,    '%']
        super(PercentageUnit, self).__init__(initial_value, magnitudes)

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
    print " Optimal Scale"
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
