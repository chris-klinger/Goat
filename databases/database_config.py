"""
This module contains code for creating the underlying database structures
and also general code to perform basic actions: add, remove, update, list
"""

import os

from settings import settings_config
from databases import database_records,database_util,database_dirfiles
from util.inputs import prompts

def get_record_db(goat_dir):
    """Gets the records database"""
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

def add_by_dir(goat_dir, target_dir=None):
    """
    Adds records for each file in a directory. If one or more
    extensions are specified, will only add files ending in those
    extensions and ignore others
    """
    exts = []
    select_files = False
    recurse = False
    if target_dir is None:
        target_dir = prompts.DirPrompt(
            message = 'Please choose a directory to add files from',
            errormsg = 'Unrecognized directory').prompt()
    recurse = prompts.YesNoPrompt(
        message = 'Would you like to add from subdirs too?').prompt()
    if recurse.lower() in {'yes','y'}:
        recurse = True
    limit = prompts.YesNoPrompt(
        message = 'Would you like to limit files?').prompt()
    if limit.lower() in {'yes','y'}:
        valids = ['file','extension','both']
        choice = prompts.LimitedPrompt(
            message = 'Limit by file, extension, or both?',
            errormsg = 'Please choose "file", "extension", or "both"',
            valids = valids).prompt()
        if choice == 'file':
            select_files = True
        elif choice == 'extension':
            exts = database_util.get_exts()
        else:
            select_files = True
            exts = database_util.get_exts()
    database_util.add_files_by_dir(goat_dir, target_dir,
            select_files, recurse, *exts)

def add_by_file(goat_dir, addfile=None):
    """Adds a record for the specified file"""
    if addfile is None:
        addfile = database_util.get_file()
    add_record(goat_dir, addfile=addfile)

def add_record(goat_dir, record=None, addfile=None, rdir=None, subdir=None):
    """
    Adds a record to the database. The user is requested to provide
    values for missing information.
    """
    records_db = get_record_db(goat_dir)
    if record is None:
        record = database_util.get_record()
    if records_db.check_record(record):
        print('Goat has detected an existing record for {}'.format(record))
        modify = prompts.YesNoPrompt(
            message = 'Do you want to modify {}?'.format(record))
        if modify in {'no','n'}:
            print('Did not modify {}'.format(record))
        elif modify in {'yes','y'}:
            update_record(goat_dir,record)
    else:
        print('No such record exists yet, adding record')
        records_db.add_record_obj(record)
    if addfile is None:
        print('Warning, no file for record {}.'
            'Goat requires files for all functionality'.format(record))
        add_now = prompts.YesNoPrompt(
            message = 'Would you like to add a file now?').prompt()
        if add_now.lower() in {'yes','y'}:
            addfile = database_util.get_file()
        elif add_now.lower() in {'no','n'}:
            pass # Might change later
    try:
        print('File to be added is {}'.format(addfile))
        database_dirfiles.add_record_from_file(goat_dir, record, addfile)
    except Exception:
        pass # Could not add file
    more_info = prompts.YesNoPrompt(
        message = 'Do you wish to add more info for record {}?'.format(record)).prompt()
    if more_info.lower() in {'no', 'n'}:
        pass # nothing more to do
    elif more_info.lower() in {'yes', 'y'}:
        records_db.extend_record(record,
            **database_util.add_attribute_loop())

def remove_record(goat_dir, record=None):
    """Removes a record from the database"""
    records_db = get_record_db(goat_dir)
    if record is None:
        record = database_util.get_record()
    user_conf = prompts.YesNoPrompt(
        message = 'Do you wish to delete all data for {}?'.format(record)).prompt()
    if user_conf.lower() in {'no', 'n'}:
        pass # nothing more to do
    elif user_conf.lower() in {'yes', 'y'}:
        records_db.remove_record_obj(record)
        database_dirfiles.remove_record_dir(goat_dir,record)

def update_record(goat_dir, record=None):
    """
    Combines user input with other functions to update records
    already present in the database
    """
    records_db = get_record_db(goat_dir)
    if record is None:
        record = database_util.get_record()
    choices = {'add', 'change', 'remove', 'quit'}
    cont = True
    while cont is True:
        user_choice = prompts.LimitedPrompt(
            message = 'Please choose an option: add, change, remove, quit',
            errormsg = 'Unrecognized option',
            valids = choices).prompt()
        if user_choice.lower() == 'quit':
            cont = False
        elif user_choice.lower() == 'add':
            records_db.extend_record(record,
                    **database_util.add_attribute_loop(
                        goat_dir,record))
        elif user_choice.lower() == 'remove':
            records_db.reduce_record(record,
                    *database_util.remove_attribute_loop(
                        goat_dir,record))
        elif user_choice.lower() =='change':
            to_change = database_util.change_attribute_loop(
                    goat_dir,record)
            for k,v in to_change.items():
                records_db.change_record_attr(record,k,v)

def check_record(goat_dir, record=None):
    """Checks whether a record is already present"""
    records_db = get_record_db(goat_dir)
    if record is None:
        record = database_util.get_record()
    if records_db.check_record(record):
        print('Record for {} exists in database'.format(record))
    else:
        print('Could not find record for {} in database'.format(record))

def list_records(goat_dir, record_type=None):
    """
    Lists records in the database, either by their attributes or by
    the included files
    """
    records_db = get_record_db(goat_dir)
    for record in records_db.list_records():
        print(record)
        records_db.list_record_info(record)
