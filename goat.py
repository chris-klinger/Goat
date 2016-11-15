#!/usr/bin/env python3

import os, sys

from bin import initialize_goat
from settings import settings_interface
from databases import database_interface
from searches import search_interface

goat_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

def main_goat():
    initialize_goat.initialize(goat_dir)
    settings_interface.settings_loop(goat_dir)
    database_interface.database_loop(goat_dir)
    search_interface.search_loop(goat_dir)

if __name__ == '__main__':
    main_goat()
