"""
This module contains code for creating the underlying database structures
and also general code to perform basic actions: add, remove, update, list
"""

import os

from settings import settings_config
#from databases import organism_database
#from util import prompts

def get_db_dir_path(goat_dir):
    """Returns full pathname to db directory"""
    return os.path.join(goat_dir, 'DB')

def check_for_dbs(goat_dir):
    """Checks whether a database folder already exists"""
    if os.path.exists(get_db_dir_path(goat_dir)):
        return True
    return False

def create_dbs(goat_dir):
    """Creates the initial database structure"""
    db_dir = get_db_dir_path(goat_dir)
    os.mkdir(db_dir)
    settings_config.add_setting(goat_dir, database_directory=db_dir)

def add_by_dir(target_dir, *exts):
    """
    Adds records for each file in a directory. If one or more
    extensions are specified, will only add files ending in those
    extensions and ignore others
    """
    pass

def recursive_add_by_dir(target_dir, *exts):
    """Recursive version of add_by_dir()"""
    pass

def add_by_file(addfile):
    """Adds a record for the specified file"""
    pass

def add_record(record=None, addfile=None, rdir=None, subdir=None):
    """
    Adds a record to the database. The user is requested to provide
    values for missing information.
    """
    pass

def remove_record(record=None):
    """Removes a record from the database"""
    pass

def update_record(record=None):
    """
    Combines user input with other functions to update records
    already present in the database
    """
    pass

def list_records(record_type=None):
    """
    Lists records in the database, either by their attributes or by
    the included files
    """
    pass
