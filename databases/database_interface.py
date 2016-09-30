"""
Interface for Goat-style database. Needs to eventually manage both a
shelve database of records along with their underlying directories
and files.
"""

from util.inputs import prompts
from databases import database_config

valid_options = {'add', 'change', 'check', 'remove', 'quit', 'list'}

def database_loop(goat_dir):
    """Accesses database based on user input"""
    loop = True
    while loop == True:
        user_input = prompts.LimitedPrompt(
            message = 'Please choose an action (add, change, check, remove, list, quit)',
            errormsg = 'Unrecognized action',
            valids = valid_options).prompt()
        if user_input == 'add':
            database_config.add_record(goat_dir)
        elif user_input == 'remove':
            database_config.remove_record(goat_dir)
        elif user_input == 'change':
            database_config.update_record(goat_dir)
        elif user_input == 'check':
            database_config.check_record(goat_dir)
        elif user_input == 'list':
            database_config.list_records(goat_dir)
        elif user_input == 'quit':
            loop = False
