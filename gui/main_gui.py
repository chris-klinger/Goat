"""
This module contains code for the main GUI screen of GOAT. The main screen acts as
a launcher to all underlying operations.
"""

from tkinter import *

def run():
    root = Tk()
    root.title('Goat')
    from gui.root import RootFrame
    RootFrame(root)
    root.mainloop()
