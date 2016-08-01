"""
Interface for generic settings file
"""

from goat.util import prompts
import config

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
            config.add_setting(goat_dir)
        elif user_input == 'change':
            config.change_setting(goat_dir)
        elif user_input == 'check':
            config.check_setting(goat_dir)
        elif user_input == 'remove':
            config.check_setting(goat_dir)
        elif user_input == 'quit':
            loop = False
