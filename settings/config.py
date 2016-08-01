"""
This module contains code for managing the underlying settings feature,
including code to create, add, remove, or change settings
"""

import os, pickle

from settings_file import Settings
from interface import SettingsFile

basename = 'goat_settings.pkl'

def check_for_settings():
    """Checks whether a settings file currently exists"""
    if os.path.exists(os.path.join(os.getcwd(),basename)):
        return True
    return False

def create_settings():
    """Creates the initial settings file"""
    with open(os.path.join(os.getcwd(),basename), 'wb') as o:
        settings = Settings()
        pickle.dump(settings, o)

def get_settings_file():  # May not need?
    """Returns full pathname of settings file"""
    return os.path.join(os.getcwd(),basename)

def add_setting(setting, value):
    """Adds to settings file"""
    settings = SettingsFile(get_settings_file())
    settings.setting = value

def remove_setting(setting):
    """Removes a setting from settings file"""
    pass

def check_setting(setting):
    """Returns current value for setting"""
    settings = SettingsFile(get_settings_file())
    return settings.setting

def change_setting(setting):
    """Changes a setting from settings file"""
    settings = SettingsFile(get_settings_file())
    settings.setting = value
