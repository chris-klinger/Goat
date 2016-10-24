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

def get_query_files():
    """Prompts user for one or more files containing query sequences"""
    query_files = []
    loop = True
    while loop:
        valids = ['add','quit']
        choice = prompts.LimitedPrompt(
            message = 'Please choose to add a query file or quit',
            errormsg = 'Please choose either "add" or "quit"',
            valids = valids).prompt()
        if choice == 'add':
            qfile = prompts.FilePrompt(
                message = 'Please choose a file with one or more query sequences',
                errormsg = 'Please choose a valid file').prompt()
            query_files.append(qfile)
        elif choice == 'quit':
            loop = False
    return query_files
