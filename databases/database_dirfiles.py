"""
This module contains code to work with the file structure underlying
database records. Most of these operations should be nearly invisible
to the user.

Note: for the directory removal operations, should import a generic
recursive directory removal from util or somewhere else and call it
"""

import os, shutil

from databases import database_config,database_util
#from util.inputs import prompts
from util.directories import walk_dirs,dirfiles
from util.exceptions import goat_exceptions

def check_record_dir(goat_dir, record=None, path=None):
    """Checks whether a directory already exists"""
    if path is not None:
        return dirfiles.check_path(path, 'dir')
    else:
        seq_db = database_config.get_db_dir_path(goat_dir)
        if record is None:
            record = database_util.get_record()
        if os.path.isdir(os.path.join(seq_db,record)):
            return True
        else:
            return False

def check_record_subdir(goat_dir, record=None, dir_type=None, path=None):
    """Checks whether a directory already exists"""
    if path is not None:
        return dirfiles.check_path(path, 'dir')
    else:
        seq_db = database_config.get_db_dir_path(goat_dir)
        if record is None:
            record = database_util.get_record()
        if dir_type is None:
            dir_type = database_util.get_dir_type()
        if os.path.isdir(os.path.join(seq_db,record,dir_type)):
            return True
        else:
            return False

def add_record_dir(goat_dir, record=None, create=False):
    """Creates a directory for the given record"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    if record is None:
        record = database_util.get_record()
    dirpath = os.path.join(seq_db, record)
    if check_record_dir(goat_dir, path=dirpath):
        raise goat_exceptions.DirExistsError(dirpath)
    else:
        if create:
            os.mkdir(dirpath)
        else:
            return dirpath

def add_record_subdir(goat_dir, record=None, dir_type=None, create=False):
    """Creates a subdirectory for the given record of the specified type.
    In future, want to implement a clause also, for if the specified record
    directory does not already exist as well?"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    if record is None:
        record = database_util.get_record()
    if dir_type is None:
        dir_type = database_util.get_dir_type()
    dirpath = os.path.join(seq_db, record, dir_type)
    if check_record_subdir(goat_dir, path=dirpath):
        raise goat_exceptions.DirExistsError(dirpath)
    else:
        if create:
            os.mkdir(dirpath)
        else:
            return dirpath

def add_file_to_subdir(subdir, addfile, mode='copy'):
    """
    Adds a file to the specified directory. Default mode is copy, but
    can also be move if the original file is not desired to be kept.
    Both subdir and addfile must be specified as whole paths.
    """
    # Does the desired file exist?
    if not dirfiles.check_path(addfile, 'file'):
        print('Goat cannot recognize file {}'.format(addfile))
    # Is the file already present in the subdir?
    if dirfiles.check_path(os.path.join(subdir,os.path.basename(addfile))):
        raise goat_exceptions.FileExistsError(os.path.join(
            subdir,os.path.basename(addfile)))
    else:
        if mode == 'copy':
            shutil.copy(addfile,subdir)
        elif mode == 'move':
            shutil.move(addfile,subdir)

def add_file_to_record(goat_dir, record, addfile, dir_type=None):
    """
    Adds the full path of the specified file to the 'dir_type' attribute
    of the corresponding record. To be used later for the purposes of
    quick file lookup.
    """
    if dir_type is None:
        dir_type = database_util.get_dir_type()
    records_db = database_config.get_record_db(goat_dir)
    to_add = {}
    to_add[dir_type] = addfile
    records_db.extend_record(record, **to_add)

def add_record_file(goat_dir, record, subdir, addfile, mode='copy'):
    """
    Adds a file, both to the record directory as well as to the
    record itself. Both subdir and addfile should be full paths.
    """
    renamed_file = os.path.join(subdir, os.path.basename(addfile))
    subdir_name = os.path.basename(subdir)
    add_file_to_subdir(subdir, addfile, mode)
    add_file_to_record(goat_dir, record, renamed_file, subdir_name)

def add_record_from_file(goat_dir, record, addfile, dir_type=None):
    """
    Adds all required dirs and subdirs for a specified file. If the
    record dir already exists, uses the existing one. If the subdir
    already exists, complains (must be unique).
    """
    try:
        add_record_dir(goat_dir, record, create=True)
    except goat_exceptions.DirExistsError as nonuniq:
        print(nonuniq)
    if dir_type is None:
        dir_type = database_util.get_dir_type()
    try:
        subdir = add_record_subdir(goat_dir,record,dir_type)
        os.mkdir(subdir)
    except goat_exceptions.DirExistsError as nonuniq:
        print(nonuniq)
    try:
        add_record_file(goat_dir, record, subdir, addfile)
    except goat_exceptions.FileExistsError as nonuniq:
        print(nonuniq)

def remove_record_dir(goat_dir, record):
    """Recursively remove all subdirs for chosen record"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    if not check_record_dir(goat_dir,record):
        print('Could not remove directory for {}, no such record'.format(
            record))
    else:
        shutil.rmtree(os.path.join(seq_db,record))

def remove_record_file(rmfile):
    """Removes a file. Both subdir and rmfile must be whole paths"""
    if not os.path.isfile(rmfile):
        print('Goat cannot recognize file {}'.format(rmfile))
    else:
        os.remove(rmfile)

def remove_record_subdir(goat_dir, record, dir_type):
    """Removes subdir and all files"""
    seq_db = database_config.get_db_dir_path(goat_dir)
    if not os.path.isdir(os.path.join(seq_db,record,dir_type)):
        print('Could not remove {} subdirectory of {}'.format(
            dir_type,record))
    else:
        shutil.rmtree(os.path.join(seq_db,record,dir_type))

def remove_subdir_attr(goat_dir, record, dir_type):
    """Removes the subdir and all files in it; also, removes corresponding
    attribute from the record object"""
    records_db = database_config.get_record_db(goat_dir)
    remove_record_subdir(goat_dir, record, dir_type)
    records_db.reduce_record(record, dir_type)

def list_record_structure(goat_dir,*args):
    """
    Will eventually implement a recursive walker class to move down
    the directory tree and list out dirs and files. Might also allow
    for restrictions, through the use of *args and/or **kwargs
    """
    seq_db = database_config.get_db_dir_path(goat_dir)
    walker = walk_dirs.SeqDBWalker(start_dir=seq_db)
    walker.run()
    print('DB has {} records containing {} files'.format(
        walker.numcounts))
