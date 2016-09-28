"""
This module contains accessory code for use in the other database modules.
"""

from util import prompts
from databases import database_config

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

def add_attribute_loop(add_dict=None):
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

def remove_attribute_loop(remove_list=None):
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

