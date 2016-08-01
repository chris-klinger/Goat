"""
Interface for generic settings file
"""

import pickle

class SettingsFile:
    """Interface for underlying settings object"""
    def __init__(self, db_name):
        self.db_name = db_name

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
