"""
This module contains new code for dealing with sets in Goat. Idea is to have a
generic set superclass with some default attributes and methods, and then to
subclass out for additional attributes/functionality.
"""

from persistent import Persistent

class Set(Persistent):
    def __init__(self, name):
        self.name = name
        self.entries = []
        self.num_entries = 0

    def add_entries(self, entry_list):
        """Adds to internal list, recalculates attr value"""
        self.entries = entry_list
        self._calc_num_entries()
        self._p_changed = 1 # ensures persistence

    def list_entries(self):
        """Convenience function"""
        return self.entries

    def _calc_num_entries(self):
        """Called on updates to recalculate attribute value"""
        self.num_entries = len(self.entries)

class QuerySet(Set):
    def __init__(self, name, query_type):
        Set.__init__(self, name)
        self.qtype = query_type

class DBSet(Set):
    def __init__(self, name):
        Set.__init__(self, name)
