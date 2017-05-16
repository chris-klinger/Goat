"""
This module contains code for dealing with viewing and updating queries
"""

from tkinter import *
from tkinter import ttk

from gui.util import input_form
from gui.util import gui_util

class QueryFrame(Frame):
    def __init__(self, query_db, record_db, parent=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.rdb = record_db
        self.pack(expand=YES, fill=BOTH)
        self.query = QueryGui(query_db, record_db, self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Add Queries', self.onAddQueries, {'side':LEFT}),
                        ('Save', self.onSave, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Done', self.onSubmit, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Signals to close associated database connections when window is closed.
        Need to implement a method of determining whether changes have occurred,
        so that closing without changing anything bypasses commit but closing after
        unsaved changes prompts user to save them or not"""
        self.qdb.close()
        self.rdb.close()
        self.parent.destroy()

    def onAddQueries(self):
        """Pops up a new window to add queries either individually or by file"""
        pass

    def onSave(self):
        """Signals to associated dbs to commit but not close"""
        pass

    def onCancel(self):
        """Closes database connections but does not commit unsaved changes"""
        pass

    def onSubmit(self):
        """Commits and closes associated databases"""
        pass

class QueryGui(ttk.Panedwindow):
    def __init__(self, query_db, record_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.query_frame = QueryListFrame(query_db, self)
        self.info_frame = QueryInfoFrame(query_db, record_db, self)
        self.add(self.query_frame)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

class QueryListFrame(Frame):
    def __init__(self, query_db, parent=None):
        Frame.__init__(self, parent)
        Label(self, text='Available Queries').pack(expand=YES, fill=X, side=TOP)
        self.query_notebook = QueryNotebook(query_db, self)
        self.toolbar1 = Frame(self)
        self.toolbar1.pack(side=BOTTOM, expand=YES, fill=X)
        #self.toolbar2 = Frame(self)
        #self.toolbar2.pack(side=BOTTOM, expand=YES, fill=X)
        self.pack(expand=YES, fill=BOTH)

        self.buttons1 = [('Add to Set', self.onAddToSet, {'side':RIGHT}),
                        ('Remove from Set', self.onRmFromSet, {'side':RIGHT}),
                        ('Add Query Set', self.onAddQSet, {'side':RIGHT}),
                        ('Remove Query Set', self.onRmQSet, {'side':RIGHT})]
        for (label, action, where) in self.buttons1:
            Button(self.toolbar1, text=label, command=action).pack(where)

        #self.buttons2 = [('Add Query Set', self.onAddQSet, {'side':RIGHT}),
        #                ('Remove Query Set', self.onRmQSet, {'side':RIGHT})]
        #for (label, action, where) in self.buttons2:
        #    Button(self.toolbar2, text=label, command=action).pack(where)

    def onAddQSet(self):
        pass

    def onRmQSet(self):
        pass

    def onAddToSet(self):
        pass

    def onRmFromSet(self):
        pass

class QueryNotebook(ttk.Notebook):
    def __init__(self, query_db, parent=None):
        ttk.Notebook.__init__(self, parent)
        self.qset = QuerySetViewer(query_db, self)
        self.qlist = QueryScrollBox(query_db, self)
        self.add(self.qset, text='Query Sets')
        self.add(self.qlist, text='All Queries')
        self.pack(expand=YES, fill=BOTH)

class QuerySetViewer(ttk.Treeview):
    def __init__(self, query_db, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)

class QueryScrollBox(Listbox):
    def __init__(self, query_db, parent=None):
        Listbox.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)

class QueryInfoFrame(Frame):
    def __init__(self, query_db, record_db, parent=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.rdb = record_db
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Query Information').pack(expand=YES, fill=X, side=TOP)
        self.name = input_form.DefaultValueForm([('Name','')],self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self, self.rdb.list_records(), # record db keys
                labeltext='Associated record')
        self.raccs = gui_util.ScrollBoxFrame(self, 'Redundant accessions', [])
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Remove', self.onRemove, {'side':RIGHT}),
                        ('Modify Raccs', self.onModify, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        """Removes the query"""
        pass

    def onModify(self):
        """Allows user to change redundant accessions"""
        pass
