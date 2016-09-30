"""
Interface for generic settings file
"""

from util.inputs import prompts
from settings import settings_config

valid_options = {'add', 'change', 'check', 'remove', 'quit', 'list'}

def settings_loop(goat_dir):
    """Accesses settings file based on user input"""
    loop = True
    while loop == True:
        user_input = prompts.LimitedPrompt(
            message = 'Please choose an action (add, change, check, remove, list, quit)',
            errormsg = 'Unrecognized action',
            valids = valid_options).prompt()
        if user_input == 'add':
            settings_config.add_setting(goat_dir)
        elif user_input == 'change':
            settings_config.change_setting(goat_dir)
        elif user_input == 'check':
            settings_config.check_setting(goat_dir)
        elif user_input == 'remove':
            settings_config.remove_setting(goat_dir)
        elif user_input == 'list':
            settings_config.list_settings(goat_dir)
        elif user_input == 'quit':
            loop = False
