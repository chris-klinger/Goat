"""
Interface for generic settings file
"""

from util import prompts
import settings.config

valid_options = {'add', 'change', 'check', 'remove', 'quit'}

def settings_loop(goat_dir):
    """Accesses settings file based on user input"""
    loop = True
    while loop == True:
        user_input = prompts.LimitedPrompt(
            message = 'Please choose an action (add, change, check, remove, quit)',
            errormsg = 'Unrecognized action',
            valids = valid_options).prompt()
        if user_input == 'add':
            settings.config.add_setting(goat_dir)
        elif user_input == 'change':
            settings.config.change_setting(goat_dir)
        elif user_input == 'check':
            settings.config.check_setting(goat_dir)
        elif user_input == 'remove':
            settings.config.check_setting(goat_dir)
        elif user_input == 'quit':
            loop = False
