"""
This module contains code for the main GUI screen of GOAT. The main screen acts as
a launcher to all underlying operations.
"""

from tkinter import *
from tkinter.messagebox import *

from settings import settings_config
from databases import database_config
from searches import search_obj
from gui.settings import settings_form
from gui.database import database_gui
from gui.searches import search_gui
from gui.results import result_gui
from gui.queries import query_gui

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
    file_menu.add_command(label='settings', command=settings_popup, underline=0)
    file_menu.add_command(label='quit', command=window.quit, underline=0)
    top.add_cascade(label='File', menu=file_menu, underline=0)

    search_menu = Menu(top, tearoff=False)
    search_menu.add_command(label='new search', command=search_popup, underline=0)
    search_menu.add_command(label='reverse search', command=reverse_search, underline=0)
    search_menu.add_command(label='search from result', command=result_search, underline=0)
    search_menu.add_command(label='run analysis', command=analysis_popup, underline=0)
    top.add_cascade(label='Search', menu=search_menu, underline=0)

    results_menu = Menu(top, tearoff=False)
    results_menu.add_command(label='view result(s)', command=result_viewer, underline=0)
    results_menu.add_command(label='sequences from result', command=result_sequences, underline=0)
    top.add_cascade(label='Results', menu=results_menu, underline=0)

    summary_menu = Menu(top, tearoff=False)
    summary_menu.add_command(label='summarize result(s)', command=summarize_results, underline=0)
    summary_menu.add_command(label='view summaries', command=summary_viewer, underline=0)
    summary_menu.add_command(label='sequences from summary', command=summary_sequences, underline=0)
    summary_menu.add_command(label='summary graphic', command=summary_graphic, underline=0)
    summary_menu.add_command(label='summary table', command=summary_table, underline=0)
    top.add_cascade(label='Summaries', menu=summary_menu, underline=0)

    query_menu = Menu(top, tearoff=False)
    query_menu.add_command(label='modify queries', command=query_popup, underline=0)
    top.add_cascade(label='Queries', menu=query_menu, underline=0)

    db_menu = Menu(top, tearoff=False)
    db_menu.add_command(label='modify databases', command=database_popup, underline=0)
    db_menu.add_command(label='database table', command=database_table, underline=0)
    top.add_cascade(label='Databases', menu=db_menu, underline=0)

def settings_popup():
   window = Toplevel()
   settings_form.SettingsForm(settings_config.list_settings(),window)

def search_popup():
    goat_db = database_config.get_goat_db()
    query_db = database_config.get_query_db(goat_db)
    record_db = database_config.get_record_db(goat_db)
    search_db = database_config.get_search_db(goat_db)
    result_db = database_config.get_result_db(goat_db)
    if askyesno(
        message='Run a reverse search?',
        icon='question', title='Reverse Search'):
        window = Toplevel()
        search_gui.ReverseSearchFrame(query_db,record_db,search_db,result_db,window)
    else: # set up a new search
        window = Toplevel()
        search_gui.SearchFrame(query_db,record_db,search_db,result_db,window)

def reverse_search():
    """Run a reverse search from an existing forward search"""
    pass

def result_search():
    """Run a forward search using queries from a previous search"""
    pass

def analysis_popup():
    """Run a full analysis, typically forward-reverse"""
    pass

def result_viewer():
    """View information for results from previous searches"""
    window = Toplevel()
    goat_db = database_config.get_goat_db()
    #query_db = database_config.get_query_db(goat_db)
    #record_db = database_config.get_record_db(goat_db)
    result_db = database_config.get_result_db(goat_db)
    search_db = database_config.get_search_db(goat_db)
    result_gui.ResultFrame(result_db, search_db, window)

def result_sequences():
    """Obtain sequence file(s) from a search result"""
    pass

def summarize_results():
    """Obtain a summary for one or more results"""
    pass

def summary_viewer():
    """View information for summaries"""
    pass

def summary_sequences():
    """Obtain sequence file(s) from a summary"""
    pass

def summary_graphic():
    """Obtain a graphical view of a summary"""
    pass

def summary_table():
    """Obtain a csv file containing summary information"""
    pass

def query_popup():
    window = Toplevel()
    goat_db = database_config.get_goat_db()
    query_db = database_config.get_query_db(goat_db)
    record_db = database_config.get_record_db(goat_db)
    query_gui.QueryFrame(query_db, record_db, window)

def database_popup():
    window = Toplevel()
    #db = database_config.get_record_db()
    #database_gui.DatabaseFrame(database_config.get_record_db(),window)
    goat_db = database_config.get_goat_db()
    record_db = database_config.get_record_db(goat_db)
    database_gui.DatabaseFrame(record_db,window)

def database_table():
    """Obtain csv-style file with information for one or more databases"""
    pass

def run():
    root = Tk()
    root.title('Goat')
    make_menu(root)
    msg = Label(root, text=help_msg)
    msg.pack(expand=YES, fill=BOTH)
    root.mainloop()
