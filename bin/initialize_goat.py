"""
Provides an initialization framework for Goat in a new directory.

Consists of the following functions:
'initialize_goat()' - runs the other two functions
'check_goat()' - checks whether a Goat subdirectory already exists and
returns True, else returns False
'make_goat()' - builds a Goat subdirectory structure if required
"""

#import os
#import goat
from settings import settings_config
from databases import database_config

def initialize(*args):
    """Runs other initialization functions"""
    initialize_settings(*args)
    #initialize_dbs(*args)

def initialize_settings():
    """Checks for a settings file"""
    if settings_config.check_for_settings():
        pass
    else:
        settings_config.create_settings()
        settings_config.add_setting(foo='bar')
        #settings_config.add_setting(,j

#def initialize_dbs(goat_dir):
    #"""Checks for required database structure"""
    #if database_config.check_for_dbs(goat_dir):
        #pass
    #else:
        #database_config.create_dbs(goat_dir)


