"""
Provides an initialization framework for Goat in a new directory.

Consists of the following functions:
'initialize_goat()' - runs the other two functions
'check_goat()' - checks whether a Goat subdirectory already exists and
returns True, else returns False
'make_goat()' - builds a Goat subdirectory structure if required
"""

#import os
from goat.settings import config

def initialize(*args):
    """Runs other initialization functions"""
    initialize_settings(*args)

def initialize_settings(goat_dir):
    """Checks for a settings file"""
    if config.check_for_settings(goat_dir):
        pass
    else:
        config.create_settings(goat_dir)


#def initialize():
#    """Builds a Goat subdirectory if one does not exist"""
#    if not check_goat():
#        make_goat()

#def check_goat():
#    """Checks the current directory for a Goat subdirectory"""
#    for elem in os.listdir():
#        if os.path.isdir(elem) and 'Goat' in elem:  # Goat subdir
#            return True
#    return False

#def make_goat():
#    """Makes a new Goat subdirectory"""
#    newfiles = ['goat_settings.txt']
#    newdirs = ['Goat_databases', 'Goat_temp']
#    curr_dir = os.getcwd()
#    os.mkdir('Goat')
#    for newfile in newfiles:
#        open(os.path.join(curr_dir, 'Goat', newfile), 'a').close()
#    for newdir in newdirs:
#        os.makedirs(os.path.join(curr_dir, 'Goat', newdir))
