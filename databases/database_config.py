"""
This module contains code for creating the underlying database structures
and also general code to perform basic actions: add, remove, update, list
"""

import os

from settings import settings_config
from databases import database_records
from util import prompts

def get_record_db(goat_dir):
    return database_records.RecordsDB(os.path.join(
        settings_config.get_setting(goat_dir, 'database_directory'),'records'))

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

def add_record(goat_dir, record=None, addfile=None, rdir=None, subdir=None):
    """
    Adds a record to the database. The user is requested to provide
    values for missing information.
    """
    records_db = get_record_db(goat_dir)
    if record is None:
        genus = prompts.StringPrompt(
            message = 'Please enter a genus name').prompt()
        species = prompts.StringPrompt(
            message = 'Please enter a species name').prompt()
        record = str(genus + '_' + species)
    if records_db.check_record(record):
        print('Goat has detected an existing record for {}'.format(record))
        pass # do something
    else:
        print('No such record exists yet, adding record')
        records_db.add_record_obj(record)
    if addfile is None:
        print('Warning, no file for record {}. Goat requires files for all functionality'.format(record))
    else:
        print('File to be added is {}'.format(addfile))
        pass # need to add directories and subdirs here later
    more_info = prompts.YesNoPrompt(
        message = 'Do you wish to add more info for records {}?'.format(record),
        errormsg = 'Please enter YES/yes/Y/y or NO/no/N/n').prompt()
    if more_info.lower() in {'no', 'n'}:
        pass # nothing more to do
    elif more_info.lower() in {'yes', 'y'}:
        pass # Need to add more functionality here eventually

def remove_record(goat_dir, record=None):
    """Removes a record from the database"""
    records_db = get_record_db(goat_dir)
    if record is None:
        genus = prompts.StringPrompt(
            message = 'Please enter a genus name').prompt()
        species = prompts.StringPrompt(
            message = 'Please enter a species name').prompt()
        record = str(genus + '_' + species)
    if records_db.check_record(record):
        user_conf = prompts.YesNoPrompt(
            message = 'Do you wish to delete all data for {}?'.format(record),
            errormsg = 'Please enter YES/yes/Y/y or NO/No/no/n').prompt()
        if user_conf.lower() in {'no', 'n'}:
            pass # nothing more to do
        elif user_conf.lower() in {'yes', 'y'}:
            records_db.remove_record_obj(record)

def update_record(record=None):
    """
    Combines user input with other functions to update records
    already present in the database
    """
    pass

def check_record(record=None):
    """Checks whether a record is already present"""
    pass

def list_records(goat_dir, record_type=None):
    """
    Lists records in the database, either by their attributes or by
    the included files
    """
    records_db = get_record_db(goat_dir)
    for record in records_db.list_records():
        print(record)
        records_db.list_record_info(record)
