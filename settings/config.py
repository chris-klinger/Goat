"""
This module contains code for managing the underlying settings feature,
including code to create, add, remove, or change settings
"""

import os, pickle

from settings_file import Settings, SettingsFile
from goat.util import prompts

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

def add_setting(goat_dir):
    """Adds to settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    to_add = prompts.StringPrompt(
        message = 'Please choose a setting to add').prompt()
    value = prompts.StringPrompt(
        message = 'Please choose a value for this setting').prompt()
    settings.to_add = value

def remove_setting(goat_dir,setting):
    """Removes a setting from settings file"""
    pass

def check_setting(goat_dir):
    """Returns current value for setting"""
    settings = SettingsFile(get_settings_file(goat_dir))
    to_check = prompts.StringPrompt(
        message = 'Please choose a setting to check').prompt()
    return settings.to_check

def change_setting(goat_dir,setting):
    """Changes a setting from settings file"""
    settings = SettingsFile(get_settings_file(goat_dir))
    to_change = prompts.StringPrompt(
        message = 'Please choose a setting to change').prompt()
    change_to = prompts.StringPrompt(
        message = 'Current value for setting {} is {}. Please choose a new value'.format(to_change, settings.to_change)).prompt()
    settings.to_change = change_to
