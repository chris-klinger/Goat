"""
This file is intended to hold a generic settings file class. The class
is intentionally empty.
"""

import pickle

class Settings:
    """Generic settings object"""
    def __init__(self):
        pass  # Initially empty

class SettingsFile:
    """Interface for underlying settings object"""
    def __init__(self, db_name=None):
        if db_name:
            # Explicit dict assignment bypasses setattr
            self.__dict__['db_name'] = db_name

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
            return sorted(settings.__dict__.items())
        except(Exception):
            print('Error when accessing settings')
        finally:
            read_file.close()
