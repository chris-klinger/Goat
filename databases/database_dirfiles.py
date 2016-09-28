"""
This module contains code to work with the file structure underlying
database records. Most of these operations should be nearly invisible
to the user.

Note: for the directory removal operations, should import a generic
recursive directory removal from util or somewhere else and call it
"""

import os

from databases import database_config,database_util
from util import prompts

def check_record_dir(goat_dir,record=None):
    """Checks whether a directory already exists"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    if record is None:
        record = database_util.get_record()
    if os.path.exists(os.path.join(seq_db,record)):
        return True
    else:
        return False

def add_record_dir(goat_dir,record=None):
    """Creates a directory for the given record"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    pass

def add_record_subdir(record, dir_type):
    """Creates a subdirectory for the given record of the specified type"""
    pass

def add_record_file(subdir, addfile, mode='copy'):
    """
    Adds a file to the specified directory. Default mode is copy, but
    can also be move if the original file is not desired to be kept
    """
    pass

def remove_record_dir(record):
    """Recursively remove all subdirs for chosen record"""
    pass

def remove_record_file(subdir, rmfile):
    """Removes just the file"""
    pass

def remove_record_subdir(record, dir_type):
    """Removes subdir and all files"""
    pass

def list_record_structure(*args):
    """
    Will eventually implement a recursive walker class to move down
    the directory tree and list out dirs and files. Might also allow
    for restrictions, through the use of *args and/or **kwargs
    """
    pass
