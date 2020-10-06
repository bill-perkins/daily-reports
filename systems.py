# ----------------------------------------------------------------------------
# System Object class:
# ----------------------------------------------------------------------------
class System:
    """ The System class:
        name
        _lcld
        add_disk(disk_name, disk_size)
        get_dsksize(disk_name)
        get_entries_count(key)
        get_entries(key)
        get_keys()
        add_usage(key, usage_list)
    """
    # class variables get shared by all instances:
    # (no class variables here)

    # ------------------------------------------------------------------------
    # __init__(name)
    # ------------------------------------------------------------------------
    def __init__(self, name):
        """ Create a system object with given name, empty local dictionary
            Entry: name = system name
        """
        self.name = name            # system name
        self._lcld = {}             # local dictionary

    # ------------------------------------------------------------------------
    # __str__() 
    # ------------------------------------------------------------------------
    def __str__(self):
        """ Stringify a system: spit out useful info
        """
        output = self.name + ': ' + self.ip_address
        return output

    # ------------------------------------------------------------------------
    # set_ip_address(ip_address)
    # ------------------------------------------------------------------------
    def set_ip_address(self, ip_address):
        """ Set the given ip_address to self.
        """
        self.ip_address = ip_address

    # ------------------------------------------------------------------------
    # get_ip_address()
    # ------------------------------------------------------------------------
    def get_ip_address(self):
        """ Retrieve the IP address for this system object.
        """
        return self.ip_address

    # ------------------------------------------------------------------------
    # set_memsize(size)
    # ------------------------------------------------------------------------
    def set_memsize(self, memsize):
        """ Set the given ip_address to self.
        """
        self.memsize = memsize

    # ------------------------------------------------------------------------
    # get_memsize()
    # ------------------------------------------------------------------------
    def get_memsize(self):
        """ Retrieve the size of the system memory.
        """
        return self.memsize

    # ------------------------------------------------------------------------
    # add_component(component_name, size=None)
    # ------------------------------------------------------------------------
    def add_component(self, component_name, size=None):
        """ Add a given component name to _lcld{}.
        """
        if component_name not in self._lcld.keys():
            self._lcld[component_name] = {'entries': []}
            if size != None:
                self._lcld[component_name]['size'] =  size
        else:
            print("    *** attempt to add component '" + component_name + "' to keys.")
            print('    *** (component_name already exists)\n')

    # ------------------------------------------------------------------------
    # get_component(component_name)
    # ------------------------------------------------------------------------
    def get_component(self, component_name):
        """ Retrieve the local dictionary value for the given component.
        """
        if component_name not in self._lcld.keys():
            print('get_component(): unknown key:', component_name)

        return self._lcld[component_name]

    # ------------------------------------------------------------------------
    # add_disk(disk_name, disk_size)
    # ------------------------------------------------------------------------
    def add_disk(self, disk_name, disk_size):
        """ Add a given disk name and size to _lcld{}.
        """
        if disk_name not in self._lcld.keys():
            self._lcld[disk_name] = {'size': disk_size, 'entries': []}
        else:
            print("    *** attempt to add filesystem '" + disk_name + "' to keys.")
            print('    *** (filesystem already exists)\n')

    # ------------------------------------------------------------------------
    # add_usage(key, usage_list)
    # ------------------------------------------------------------------------
    def add_usage(self, key, usage_list):
        """ Add a usage list to a given key (system component).
            A usage list will typically be [date, time, usage]
            or maybe [dtobj, [components of message]]
        """
        if key in self._lcld.keys():
            self._lcld[key]['entries'].append(usage_list)
        else:
            print("    *** attempt to add usages for unknown key '" + key + '.')
            print('    *** (key does not exist)\n')

    # ------------------------------------------------------------------------
    # get_dsksize(disk_name)
    # ------------------------------------------------------------------------
    def get_dsksize(self, disk_name):
        """ Return size of given disk.
        """
        if disk_name in self._lcld.keys():
            return self._lcld[disk_name]['size']

    # ------------------------------------------------------------------------
    # get_keys()
    # ------------------------------------------------------------------------
    def get_keys(self):
        """ Return list of keys we have.
        """
        return self._lcld.keys()

    # ------------------------------------------------------------------------
    # get_dskkeys()
    # ------------------------------------------------------------------------
    def get_dskkeys(self):
        """ Return list of disks we have.
        """
        dskeys = []
        keylist = self.get_keys()
        dskeys = [key for key in keylist if '/' in key]

        return dskeys

    # ------------------------------------------------------------------------
    # get_entries_count(key)
    # ------------------------------------------------------------------------
    def get_entries_count(self, key):
        """ Return # of entries of given disk (or whatever).
        """
        if key in self._lcld.keys():
            dptr = self._lcld[key]
            if type(dptr) == type({}) and 'entries' in dptr.keys():
                return len(dptr['entries'])

    # ------------------------------------------------------------------------
    # get_entries(key)
    # ------------------------------------------------------------------------
    def get_entries(self, key):
        """ Return list of entries for given disk (or whatever).
        """
        if key in self._lcld.keys():
            dptr = self._lcld[key]
            if type(dptr) == type({}) and 'entries' in dptr.keys():
                return dptr['entries']
            else:
                return dptr

    # ------------------------------------------------------------------------
    # 
    # ------------------------------------------------------------------------

# EOF:
