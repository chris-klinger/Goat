#!/usr/bin/env python3

import os, sys

from bin import initialize_goat
from gui import main_gui

goat_dir = os.path.dirname(os.path.realpath(sys.argv[0]))

def goat_gui():
    initialize_goat.initialize(goat_dir)
    main_gui.run()

if __name__ == '__main__':
    goat_gui()
