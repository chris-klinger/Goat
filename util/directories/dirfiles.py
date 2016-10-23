"""
This module contains general code pertaining to directories and files
in Goat.
"""

import os

def check_path(inpath, wanted=None):
    """Checks whether a given path returns the specified type"""
    if wanted == 'file':
        if os.path.isfile(inpath):
            return True
    elif wanted == 'dir':
        if os.path.isdir(inpath):
            return True
    elif wanted is None: # is anything there?
        if os.path.exists(inpath):
            return True
    return False
