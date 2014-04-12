'''
Created on Nov 14, 2013

@license: GPLv3
@author: NSTS Contributors (see AUTHORS.txt)
'''
from collections import OrderedDict

class OptionError(RuntimeError):
    pass

class UnknownOptionError(OptionError):
    
    def __init__(self, opt_id):
        super(UnknownOptionError, self).__init__("There is no option with id '{0}'".format(opt_id))

class OptionValueDescriptor(object):
    '''
    Descriptor of an option value
    '''
    def __init__(self, option_id, help, type, default = None):
        assert isinstance(help, basestring)
        self.__id = str(option_id)
        self.__help = help
        self.__type = type
        self.__default = None if default is None else self.type(default) 
    
    @property
    def id(self):
        '''
        Get the id of this option
        '''
        return self.__id
    
    @property
    def help(self):
        '''
        Get a help string, describing usage of this option
        '''
        return self.__help
    
    @property
    def type(self):
        '''
        Get the type of this option
        '''
        return self.__type

    @property
    def default(self):
        '''
        Get the default value
        '''
        return self.__default
    
class OptionsDescriptor(object):
    '''
    A descriptor of an options container
    '''
    def __init__(self):
        self.__supported = OrderedDict()

    @property
    def supported(self):
        '''
        Get the dictionary with the supported 
        options
        '''
        return self.__supported
    
    def add_option(self, option_id, help, unit_type, default = None):
        '''
        Declare a supported option
        @param option_id The identifier of the option
        @param help A help string for the end user
        @param unit_type The type of this value
        '''
        self.__supported[option_id] = OptionValueDescriptor(option_id, help, unit_type, default)
    
    def __getitem__(self, option_id):
        '''
        Get value of specific option
        @param option_id The id of the option
        '''
        if option_id not in self.__supported.keys():
            raise UnknownOptionError(option_id)
        return self.__supported[option_id]

    def __len__(self):
        return len(self.__supported)
    
    def __iter__(self):
        return iter(self.__supported.keys())
    
class Options(object):
    '''
    A container of options that permit extensive
    description of each entry.
    '''
    def __init__(self, descriptor, values = {}):
        if not isinstance(descriptor, OptionsDescriptor):
            raise TypeError("{0} is not instance of OptionsDescriptor".format(descriptor))
        self.__supported = descriptor
        self.__values = OrderedDict()
        
        for option_id in self.__supported:
            self.__values[option_id] = self.__supported[option_id].default
        
        # Initialize with values
        if not isinstance(values, dict):
            raise TypeError("{0} is not instance of dictionary".format(values))
        for opt_id in values:
            self[opt_id] = values[opt_id]

    @property
    def supported(self):
        '''
        Get the supported descriptor
        '''
        return self.__supported

    def __getitem__(self, option_id):
        '''
        Get value of specific option
        @param option_id The id of the option
        '''
        if option_id not in self.__supported:
            raise UnknownOptionError(option_id)
        
        return self.__values[option_id]
    
    def __setitem__(self, option_id, value):
        '''
        Set value of specific option
        '''
        if option_id not in self.__supported:
            raise UnknownOptionError(option_id)
        
        self.__values[option_id] = self.__supported[option_id].type(value)
        
    def __len__(self):
        return len(self.__values)
    
    def __iter__(self):
        return iter(self.__values.keys())