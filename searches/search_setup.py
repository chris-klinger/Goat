"""
Module explanation.
"""

import pickle

class Search:
    """Generic search object. Interaction is through a separate class."""
    def __init__(self, search_type, queries, databases, *params):
        self.search_type = search_type
        self.queries = queries # pointer to the shelve object containing the instances
        self.databases = databases
        self.params = params

class SearchFile:
    """Interface for the underlying search object"""
    def __init__(self, search_name):
        self.__dict__['search_name'] = search_name

    def run():
        """Runs the actual search specified by the search file"""
        pass

    def parse():
        """Parses the search output"""
        pass

    def execute():
        """Convenience function to run searches and parse output"""
        pass

    def __getattr__(self, attr):
        """Gets attribute from settings object"""
        try:
            settings_file = open(self.db_name, 'rb')
            settings = pickle.load(settings_file)
            return getattr(settings, attr)
        except(AttributeError):
            print('No such setting as {}'.format(attr))
        finally:
            settings_file.close()

    def __setattr__(self, attr, value):
        """Sets attributes of settings object"""
        read_file = open(self.db_name, 'rb')
        settings = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.db_name, 'wb')
            setattr(settings, attr, value)
            pickle.dump(settings, write_file)
        except(Exception):
            print('Error when writing setting {}'.format(attr))
        finally:
            write_file.close()

    def __delattr__(self, attr):
        """Deletes attribute from settings object"""
        read_file = open(self.db_name, 'rb')
        settings = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.db_name, 'wb')
            delattr(settings, attr)
            pickle.dump(settings, write_file)
        except(Exception):
            print('Error when deleting setting {}'.format(attr))
        finally:
            write_file.close()

    def list_attrs(self):
        """Returns a list of all attributes from settings object"""
        read_file = open(self.db_name, 'rb')
        settings = pickle.load(read_file)
        try:
            return settings.__dict__.items()
        except(Exception):
            print('Error when accessing settings')
        finally:
            read_file.close()
