"""
This module contains utility code associated with searching operations
in Goat.
"""

from util.input import prompts

def name_search():
    """Prompts user for a name for a search"""
    loop = True
    while loop:
        search_name = prompts.StringPrompt(
            message = 'Please enter a name for this search').prompt()
        good_name = prompts.YesNoPrompt(
            message = 'Is this ok?').prompt()
        if good_name.lower() in {'yes','y'}:
            loop = False
        else:
            pass
    return search_name

def specify_search_dir():
    """Prompts user for a parent directory for searches"""
    search_dir = prompts.DirPrompt(
        message = 'Please enter a directory to add searches to',
        errormsg = 'Please enter a valid directory').prompt()
    return search_dir
