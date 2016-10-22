"""
This module contains accessory code for use in the other database modules.
"""

from util.inputs import prompts
from util.directories import walk_dirs
from databases import database_config, database_dirfiles

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_file_types = {'protein','genomic'}

def get_record(mode=None):
    """
    Prompts user for input of either a record, or alternatively for
    both the genus and species associated with a record.
    """
    if mode is None:
        valids = ['name', 'taxinfo']
        choice = prompts.LimitedPrompt(
            message = 'Select record by "name" or "taxinfo"?',
            errormsg = 'Please choose either "name" or "taxinfo"',
            valids = valids).prompt()
        mode = choice
    if mode == 'name':
        record = prompts.RecordPrompt(
            message = 'Please enter a record name').prompt()
    elif mode == 'taxinfo':
        genus = prompts.StringPrompt(
            message = 'Please enter a genus name').prompt()
        species = prompts.StringPrompt(
            message = 'Please enter a species name').prompt()
        record = str(genus + '_' + species)
    return record

def get_exts(exts=None):
    """Prompt user for one or more file extensions"""
    if exts is None:
        exts = []
    loop = True
    while loop:
        valids = ['add','quit']
        choice = prompts.LimitedPrompt(
            message = 'Please choose to add an extension or quit',
            errormsg = 'Please choose either "add" or "quit"',
            valids = valids).prompt()
        if choice.lower() == 'add':
            ext = prompts.StringPrompt(
                message = 'Please type a file extension to search for',
                errormsg = 'Unrecognized choice').prompt()
            exts.append(ext)
        elif choice.lower() == 'quit':
            loop = False
    return exts

def add_files_by_dir(goat_dir, target_dir, select_files=False,
        recurse=False, *exts):
    """
    Adds file from a specified directory to the database. Deeper subdirs
    can also be traversed for files. User specification can also extend
    to selecting each file individually, to only recognizing files with
    a specified extension, or a combination of both
    """
    file_walker = walk_dirs.FileWalker(target_dir, recurse, *exts)
    files_to_add = file_walker.getfiles()
    if not select_files:
        for addfile in files_to_add:
            print('Adding {}'.format(addfile))
            database_config.add_by_file(goat_dir, addfile)
    else:
        for addfile in files_to_add:
            user_conf = prompts.YesNoPrompt(
                message = 'Add {} to database?'.format(addfile)).prompt()
            if user_conf.lower() in {'yes','y'}:
                print('Adding {}'.format(addfile))
                database_config.add_by_file(goat_dir, addfile)
            else:
                pass # do not add the file

def add_files_by_dir_old(goat_dir, target_dir, select_files=False,
        recurse=False, *exts):
    """
    Adds files from a specified directory to the database. Deeper subdirs
    can also be traversed for files if desired. User specification can
    also extend to selecting each file individually, to only recognizing
    files with a specified extension, or a combination of both.
    """
    import os, glob
    files_to_add = []
    if not exts: # empty list
        if not recurse:
            pathname = os.path.join(target_dir, '*')
            for addfile in glob.glob(pathname):
                if os.path.isfile:
                    files_to_add.append(addfile)
        elif recurse:
            pathname = os.path.join(target_dir, '**')
            for addfile in glob.glob(pathname, recursive=True):
                if os.path.isfile:
                    files_to_add.append(addfile)
    else:
        for ext in exts:
            if '.' in ext: # user may or may not include period symbol
                ext = str(ext)
            else:
                ext = '.' + str(ext)
            if not recurse:
                pathname = os.path.join(target_dir, '*', ext)
                for addfile in glob.glob(pathname):
                    files_to_add.append(addfile)
            elif recurse:
                pathname = os.path.join(target_dir, '**', ext)
                for addfile in glob.glob(pathname,
                        recursive=True):
                    files_to_add.append(addfile)
    if not select_files:
        for addfile in files_to_add:
            print('Adding {}'.format(addfile))
            database_config.add_by_file(goat_dir, addfile)
    else:
        for addfile in files_to_add:
            user_conf = prompts.YesNoPrompt(
                message = 'Add {} to database?'.format(addfile)).prompt()
            if user_conf.lower() in {'yes','y'}:
                print('Adding {}'.format(addfile))
                database_config.add_by_file(goat_dir, addfile)
            else:
                pass # do not add the file

def get_dir_type(addfile=None):
    """
    Prompts user for input of a directory type associated with a file,
    i.e. protein or genomic.
    """
    if addfile is not None:
        dir_type = prompts.LimitedPrompt(
            message = 'Please choose a type for {}'.format(addfile),
            valids = valid_file_types).prompt()
    else:
        dir_type = prompts.LimitedPrompt(
            message = 'Please choose a type',
            valids = valid_file_types).prompt()
    return dir_type

def get_file():
    """Prompts user for input of a valid file"""
    addfile = prompts.FilePrompt(
        message = 'Please enter a file to add',
        errormsg = 'Could not recognize specified file').prompt()
    return addfile

def add_attribute_loop(goat_dir, record, add_dict=None):
    """
    Collects multiple key,value pairs to update a record object. As many
    such pairs as desired can be added before quitting.
    """
    if add_dict is None:
        add_dict = {}
    loop = True
    while loop is True:
        attr = prompts.StringPrompt(
            message = 'Please specify an attribute to add').prompt()
        if attr in valid_file_types:
            add_file = prompts.YesNoPrompt(
                message = 'Do you wish to add a file?').prompt()
            if add_file.lower() in {'yes','y'}:
                value = get_file()
                database_dirfiles.add_record_from_file(goat_dir,
                    record, value, attr)
            elif add_file.lower() in {'no','n'}:
                break
        else:
            value = prompts.StringPrompt(
                message = 'Please specify a value for {}'.format(attr)).prompt()
            user_conf = prompts.YesNoPrompt(
                message = 'You have entered {} {}, is this correct?'.format(
                    attr,value)).prompt()
            if user_conf.lower() in {'yes','y'}:
                add_dict[attr] = value
            elif user_conf.lower() in {'no','n'}:
                print('Attribute {} will not be added'.format(attr))
        cont = prompts.YesNoPrompt(
            message = 'Do you wish to add more attributes?').prompt()
        if cont.lower() in {'yes','y'}:
            pass # keep looping
        elif cont.lower() in {'no','n'}:
            loop = False
    return add_dict

def remove_attribute_loop(goat_dir, record, remove_list=None):
    """
    Collects multiple attributes to remove from a record object. As many
    such attributes as desired can be added before quitting.
    """
    if remove_list is None:
        remove_list = []
    loop = True
    while loop is True:
        attr = prompts.StringPrompt(
            message = 'Please specify an attribute to remove').prompt()
        if attr in valid_file_types:
            rm_file = prompts.YesNoPrompt(
                message = 'Do you wish to remove file for {}?'.format(
                    attr)).prompt()
            if rm_file.lower() in {'yes','y'}:
                # Only one file per subdir, therefore remove whole thing
                database_dirfiles.remove_subdir_attr(goat_dir,
                    record, attr)
            elif rm_file.lower() in {'no','n'}:
                break
        else:
            user_conf = prompts.YesNoPrompt(
                message = 'You have entered {}, is this correct?'.format(
                    attr)).prompt()
            if user_conf.lower() in {'yes','y'}:
                remove_list.append(attr)
            elif user_conf.lower() in {'no','n'}:
                print('Attribute {} will not be removed'.format(attr))
        cont = prompts.YesNoPrompt(
            message = 'Do you wish to remove more attributes?').prompt()
        if cont.lower() in {'yes','y'}:
            pass # keep looping
        elif cont.lower() in {'no','n'}:
            loop = False
    return remove_list

def change_attribute_loop(goat_dir,record,change_dict=None):
    """
    Builds up a dictionary of attributes to change based on user input.
    For each attribute, checks the current value and prompts for change
    or not. If the attribute is to be changed, further requests a new
    value for the attribute.
    """
    records_db = database_config.get_record_db(goat_dir)
    if change_dict is None:
        change_dict = {}
    loop = True
    while loop is True:
        attr = prompts.StringPrompt(
            message = 'Please specify an attribute to change').prompt()
        if attr in valid_file_types:
            change_file = prompts.YesNoPrompt(
                message = 'Current {} file is {}, do you want to change it?'.format(
                    attr, records_db.check_record_attr(record,attr))).prompt()
            if change_file.lower() in {'yes','y'}:
                # Remove the whole subdir first
                database_dirfiles.remove_subdir_attr(goat_dir,
                        record, attr)
                # Now add a new file
                new_file = get_file()
                database_dirfiles.add_record_from_file(goat_dir,
                    record, new_file, attr)
            elif change_file.lower() in {'no','n'}:
                break
        else:
            user_conf = prompts.YesNoPrompt(
                message = 'Current value for {} is {}. Do you want to change it?'.format(
                    attr, records_db.check_record_attr(record,attr))).prompt()
            if user_conf.lower() in {'no','n'}:
                print('Did not change value for {}'.format(attr))
            elif user_conf.lower() in {'yes','y'}:
                new_value = prompts.StringPrompt(
                    message = 'Please choose a new value for {}'.format(attr)).prompt()
                user_conf = prompts.YesNoPrompt(
                    message = 'New value {} ok?'.format(new_value)).prompt()
                if user_conf.lower() in {'yes','y'}:
                    change_dict[attr] = new_value
                elif user_conf.lower() in {'no','n'}:
                    print('Did not change value for {}'.format(attr))
        cont = prompts.YesNoPrompt(
            message = 'Do you wish to change more attributes?').prompt()
        if cont.lower() in {'yes','y'}:
            pass # keep looping
        elif cont.lower() in {'no','n'}:
            loop = False
    return change_dict

