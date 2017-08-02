"""
This module contains the code for the main root window of Goat.
"""

from tkinter import *
from tkinter.messagebox import *

from bin.initialize_goat import configs

from settings import settings_config
from gui.settings import settings_form
from gui.database import database_gui
from gui.searches import search_gui
from gui.results import result_gui
from gui.queries import query_gui
from gui.summaries import summary_gui

help_msg="""
Goat: an integrated platform for bioinformatic sequence analysis

Written by Christen M. Klinger

cklinger@ualberta.ca
"""

class RootFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        # Make parent window close databases
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)
        # Add menu options
        self.make_menu()
        # Fill window with some information
        Label(self, text=help_msg).pack()
        # Finally, pack window to display
        self.pack(expand=YES, fill=BOTH)

        # Keep track of whether or not windows are open

        # add current value of root to configs
        configs['root'] = self

    def onClose(self):
        """Make sure to close the connection to the main database"""
        # First check if any threads are running
        if configs['threads'].exist():
            pass # freak out
        # import configs after instantiation so they are actually populated
        configs['goat_db'].close()
        # now destroy the window
        self.parent.destroy()

    def make_menu(self):
        top = Menu(self.parent) # top-level window
        self.parent.config(menu=top) # set the menu option

        file_menu = Menu(top)
        file_menu.add_command(label='settings',
                command=self.settings_popup, underline=0)
        file_menu.add_command(label='quit',
                command=self.onClose, underline=0)
        top.add_cascade(label='File', menu=file_menu, underline=0)

        search_menu = Menu(top, tearoff=False)
        search_menu.add_command(label='new search',
                command=self.search_popup, underline=0)
        search_menu.add_command(label='reverse search',
                command=self.reverse_search, underline=0)
        search_menu.add_command(label='search from result',
                command=self.result_search, underline=0)
        search_menu.add_command(label='run analysis',
                command=self.analysis_popup, underline=0)
        top.add_cascade(label='Search', menu=search_menu, underline=0)

        results_menu = Menu(top, tearoff=False)
        results_menu.add_command(label='view result(s)',
                command=self.result_viewer, underline=0)
        results_menu.add_command(label='sequences from result',
                command=self.result_sequences, underline=0)
        top.add_cascade(label='Results', menu=results_menu, underline=0)

        summary_menu = Menu(top, tearoff=False)
        summary_menu.add_command(label='summarize result(s)',
                command=self.summarize_results, underline=0)
        summary_menu.add_command(label='view summaries',
                command=self.summary_viewer, underline=0)
        summary_menu.add_command(label='sequences from summary',
                command=self.summary_sequences, underline=0)
        summary_menu.add_command(label='summary graphic',
                command=self.summary_graphic, underline=0)
        summary_menu.add_command(label='summary table',
                command=self.summary_table, underline=0)
        top.add_cascade(label='Summaries', menu=summary_menu, underline=0)

        query_menu = Menu(top, tearoff=False)
        query_menu.add_command(label='modify queries',
                command=self.query_popup, underline=0)
        top.add_cascade(label='Queries', menu=query_menu, underline=0)

        db_menu = Menu(top, tearoff=False)
        db_menu.add_command(label='modify databases',
                command=self.database_popup, underline=0)
        db_menu.add_command(label='database table',
                command=self.database_table, underline=0)
        top.add_cascade(label='Databases', menu=db_menu, underline=0)

    def settings_popup(self):
        window = Toplevel()
        settings_form.SettingsForm(settings_config.list_settings(),window)

    def search_popup(self):
        window = Toplevel()
        search_gui.SearchFrame(window)

    def reverse_search(self):
        """Run a reverse search from an existing forward search"""
        window = Toplevel()
        search_gui.ReverseSearchFrame(window)

    def result_search(self):
        """Run a forward search using queries from a previous search"""
        pass

    def analysis_popup(self):
        """Run a full analysis, typically forward-reverse"""
        pass

    def result_viewer(self):
        """View information for results from previous searches"""
        window = Toplevel()
        result_gui.ResultFrame(window)

    def result_sequences(self):
        """Obtain sequence file(s) from a search result"""
        pass

    def summarize_results(self):
        """Obtain a summary for one or more results"""
        window = Toplevel()
        summary_gui.SearchSummaryFrame(window)

    def summary_viewer(self):
        """View information for summaries"""
        window = Toplevel()
        summary_gui.SummaryFrame(window)

    def summary_sequences(self):
        """Obtain sequence file(s) from a summary"""
        pass

    def summary_graphic(self):
        """Obtain a graphical view of a summary"""
        pass

    def summary_table(self):
        """Obtain a csv file containing summary information"""
        window = Toplevel()
        summary_gui.TableFrame(window)

    def query_popup(self):
        window = Toplevel()
        query_gui.QueryFrame(window)

    def database_popup(self):
        window = Toplevel()
        database_gui.DatabaseFrame(window)

    def database_table(self):
        """Obtain csv-style file with information for one or more databases"""
        pass
