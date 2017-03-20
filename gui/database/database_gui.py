"""
This module contains code for dealing with viewing and updating databases
"""

from tkinter import *
from tkinter import ttk

from databases import database_records

# holds a set of types for files
# note, these act as reserved keywords for Goat record attributes
valid_file_types = {'protein','genomic'}

class DatabaseGui(ttk.Panedwindow):
    def __init__(self, database, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        # assign an instance variable, pass in self as the parent to child widgets
        self.db_viewer = DatabaseViewer(database,self)
        self.info_panel = InfoPanel(self)
        self.add(self.db_viewer)
        self.add(self.info_panel)
        self.pack(expand=YES,fill=BOTH)

class DatabaseViewer(ttk.Treeview):
    def __init__(self, database, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.db = database
        self.make_tree()

    def make_tree(self):
        for record in self.db.list_records():
            #print(record)
            record_obj = self.db.fetch_record(record)
            record_name = record_obj.genus + ' ' + record_obj.species
            self.insert('','end',record,text=record_name)
            for k,v in self.db.list_record_info(record):
                if k in valid_file_types:
                    self.insert(record,'end',(record + '_' + k),text=k)


class InfoPanel(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
