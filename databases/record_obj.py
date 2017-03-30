"""
This module contains code for a new implementation of record objects. In this
instance, records are more or less simply a container for various attributes
and the majority of methods for acting on records will be encapsulated in the
database class itself.
"""

from persistent import Persistent

from databases import record_file

class Record(Persistent):
    """
    Generic record class, with a number of default attributes but also the ability
    to add more if required. Generally, attributes will be changed through the
    database instance to manage atomicity of transactions.
    """
    def __init__(self, identity=None, genus='', species='', strain='', supergroup=''):
        self.identity = identity # used for managing records
        self.genus = genus
        self.species = species
        self.strain = strain
        self.supergroup = supergroup
        self.files = {} # initialize an empty list

    def add_file(self, name, filepath, **kwargs):
        new_file = record_file.File(name, filepath, **kwargs)
        self.files[name] = new_file
        self._p_changed = 1 # else does not update

    def remove_file(self, name):
        del self.files[name]
        self._p_changed = 1

    def update_file(self, name, **kwargs):
        """Updates a file from a new set of attr/value pairs"""
        if name in self.files.keys():
            file_obj = self.files[name]
            for attr,value in kwargs:
                setattr(file_obj, attr, value)
            self._p_changed = 1
