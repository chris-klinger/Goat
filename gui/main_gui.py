"""
This module contains code for the main GUI screen of GOAT. The main screen acts as
a launcher to all underlying operations.
"""

from tkinter import *
from tkinter.messagebox import *

from settings import settings_config
from databases import database_config
from gui.settings import settings_form
from gui.database import database_gui

help_msg="""
Goat: an integrated platform for bioinformatic sequence analysis

Written by Christen M. Klinger

cklinger@ualberta.ca
"""

def not_available():
    showerror('Sorry, this is not yet implemented')

def make_menu(window):
    top = Menu(window) # top-level window
    window.config(menu=top) # set the menu option

    file_menu = Menu(top)
    file_menu.add_command(label='settings...', command=settings_popup, underline=0)
    file_menu.add_command(label='quit...', command=window.quit, underline=0)
    top.add_cascade(label='File', menu=file_menu, underline=0)

    search_menu = Menu(top, tearoff=False)
    search_menu.add_command(label='new search...', command=not_available, underline=0)
    top.add_cascade(label='Search', menu=search_menu, underline=0)

    db_menu = Menu(top, tearoff=False)
    db_menu.add_command(label='add database...', command=database_popup, underline=0)
    top.add_cascade(label='Databases', menu=db_menu, underline=0)

def settings_popup():
   window = Toplevel()
   settings_form.SettingsForm(settings_config.list_settings(),window)

def database_popup():
    window = Toplevel()
    database_gui.DatabaseGui(database_config.get_record_db(),window)


def run():
    root = Tk()
    root.title('Goat')
    make_menu(root)
    msg = Label(root, text=help_msg)
    msg.pack(expand=YES, fill=BOTH)
    root.mainloop()