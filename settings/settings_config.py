"""
This module contains code for managing the underlying settings feature,
including code to create, add, remove, or change settings
"""

import os, pickle

from settings.settings_file import Settings, SettingsFile
from util import prompts

basename = 'settings/goat_settings.pkl'

def get_settings_file(goat_dir):
    """Returns full pathname to settings file"""
    return os.path.join(goat_dir, basename)

def check_for_settings(goat_dir):
    """Checks whether a settings file currently exists"""
    if os.path.exists(get_settings_file(goat_dir)):
        return True
    return False

def create_settings(goat_dir):
    """Creates the initial settings file"""
    with open(get_settings_file(goat_dir), 'wb') as o:
        settings = Settings()
        pickle.dump(settings, o)

def add_setting(goat_dir, **kwargs):
    """Adds to settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    if len(kwargs) == 0:
        to_add = prompts.StringPrompt(
            message = 'Please choose a setting to add').prompt()
        value = prompts.StringPrompt(
            message = 'Please choose a value for this setting').prompt()
        settings.__setattr__(to_add, value)
    else:
        for key, value in kwargs.items():
            settings.__setattr__(key, value)

def remove_setting(goat_dir, *args):
    """Removes a setting from settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    if len(args) == 0:
        to_del = prompts.StringPrompt(
            message = 'Please choose a setting to delete').prompt()
        settings.__delattr__(to_del)
    else:
        for setting in args:
            settings.__delattr__(setting)

def check_setting(goat_dir, *args):
    """Returns current value for setting"""
    settings = SettingsFile(get_settings_file(goat_dir))
    if len(args) == 0:
        to_check = prompts.StringPrompt(
            message = 'Please choose a setting to check').prompt()
        if settings.__getattr__(to_check) is not None:
            print(settings.__getattr__(to_check))
    else:
        for setting in args:
            if settings.__getattr__(setting) is not None:
                print(settings.__getattr__(setting))

def change_setting(goat_dir):
    """Changes a setting from settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    to_change = prompts.StringPrompt(
        message = 'Please choose a setting to change').prompt()
    change_to = prompts.StringPrompt(
        message = 'Current value for setting "{}" is "{}". Please choose a new value'\
                .format(to_change, settings.__getattr__(to_change))).prompt()
    settings.__setattr__(to_change, change_to)

def list_settings(goat_dir):
    """Lists all current settings from settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    for key, value in settings.list_attrs():
        print('Setting {} has current value {}'.format(key,value))

def get_setting(goat_dir, setting):
    """Returns current value for a setting"""
    settings = SettingsFile(get_settings_file(goat_dir))
    try:
        return settings.__getattr__(setting)
    except(Exception):
        return None
