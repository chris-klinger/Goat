"""
This module contains code for managing the underlying settings feature,
including code to create, add, remove, or change settings
"""

import os, pickle

import goat
from settings.settings_file import SettingsFile
from util.inputs import prompts

def add_setting(**kwargs):
    """Adds to settings file"""
    settings = SettingsFile(get_settings_file())
    if len(kwargs) == 0:
        to_add = prompts.StringPrompt(
            message = 'Please choose a setting to add').prompt()
        value = prompts.StringPrompt(
            message = 'Please choose a value for this setting').prompt()
        settings.__setattr__(to_add, value)
    else:
        for key, value in kwargs.items():
            settings.__setattr__(key, value)

def remove_setting(*args):
    """Removes a setting from settings file"""
    settings = SettingsFile(get_settings_file())
    if len(args) == 0:
        to_del = prompts.StringPrompt(
            message = 'Please choose a setting to delete').prompt()
        settings.__delattr__(to_del)
    else:
        for setting in args:
            settings.__delattr__(setting)

def check_setting(*args):
    """Returns current value for setting"""
    settings = SettingsFile(get_settings_file())
    if len(args) == 0:
        to_check = prompts.StringPrompt(
            message = 'Please choose a setting to check').prompt()
        if settings.__getattr__(to_check) is not None:
            print(settings.__getattr__(to_check))
    else:
        for setting in args:
            if settings.__getattr__(setting) is not None:
                print(settings.__getattr__(setting))

def change_setting(to_change=None, change_to=None):
    """Changes a setting from settings file"""
    settings = SettingsFile(get_settings_file())
    if not to_change:
        to_change = prompts.StringPrompt(
            message = 'Please choose a setting to change').prompt()
    if not change_to:
        change_to = prompts.StringPrompt(
            message = 'Current value for setting "{}" is "{}". Please choose a new value'\
                .format(to_change, settings.__getattr__(to_change))).prompt()
    settings.__setattr__(to_change, change_to)

def list_settings():
    """Utility function"""
    settings = SettingsFile(get_settings_file())
    return settings.list_attrs()

def display_settings():
    """Lists all current settings from settings file"""
    for key, value in list_settings():
        print('Setting {} has current value {}'.format(key,value))

def get_setting(setting):
    """Returns current value for a setting"""
    settings = SettingsFile(get_settings_file())
    try:
        return settings.__getattr__(setting)
    except(Exception):
        return None
