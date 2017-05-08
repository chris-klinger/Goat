"""
This module contains code for a GUI frontend for searches
"""

import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox

from gui.util import input_form
#from gui.database import database_gui

class SearchFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.search = SearchGui(self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Cancel', self.onClose, {'side':RIGHT}),
                        ('Run', self.onRun, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        self.parent.destroy()

    def onRun(self):
        pass

class SearchGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = ParamFrame(self)
        self.query_frame = QueryFrame(self)
        self.db_frame = DatabaseFrame(self)
        self.add(self.param_frame)
        self.add(self.query_frame)
        self.add(self.db_frame)
        self.pack(expand=YES, fill=BOTH)

class ParamFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        #self.pack(expand=YES, fill=BOTH)
        self.pack()
        self.curdir = os.getcwd()
        self.entries = input_form.DefaultValueForm([('Name',''), ('Location',self.curdir)],
                self, [('Choose Directory', self.onChoose, {'side':RIGHT})])
        self.algorithm = AlgorithmFrame(self, [('Blast','blast'),('HMMer','hmmer')])
        self.keep_output = KeepOutputFrame(self)

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.insert(0,dirpath)

class AlgorithmFrame(Frame):
    def __init__(self, parent=None, choices=None):
        Frame.__init__(self, parent)
        self.choices = choices
        #self.pack(expand=YES, fill=BOTH)
        self.pack()
        Label(self, text='Algorithm').pack()
        self.algorithm = StringVar()
        for text,var in self.choices:
            ttk.Radiobutton(self, text=text, variable=self.algorithm,
                            value=var).pack(side=LEFT)
        self.algorithm.set(var) # set to last value

class KeepOutputFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        #self.pack(expand=YES, fill=BOTH)
        self.pack()
        Label(self, text='Keep output files?').pack()
        self.checked = IntVar()
        self.checkbutton = ttk.Checkbutton(self, text='Yes',
                        variable=self.checked).pack()

class ScrollBoxFrame(Frame):
    def __init__(self, parent=None, text=None, items=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        if text:
            Label(self, text=text).pack(side=TOP)
        self.item_list = [] # internal list mapping to listbox list
        self.item_dict = {} # hashtable for listbox items
        self.listbox = Listbox(self, height=20,
                            selectmode='extended' # choose multiple items at once
                            )
        self.listbox.pack(side=LEFT)
        vs = ttk.Scrollbar(self, orient=VERTICAL, command=self.listbox.yview)
        vs.pack(side=RIGHT)
        self.listbox['yscrollcommand'] = vs.set
        if items:
            for item,value in items:
                self.listbox.insert('end', item)
                self.item_list.append(item)
                self.item_dict[item] = value

class QueryFrame(Frame):
    def __init__(self, parent=None, text='Queries', items=None):
        Frame.__init__(self, parent)
        self.querybox = ScrollBoxFrame(self, text, items)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)
        self.buttons=[('Remove', self.onRemove, {'side':RIGHT}),
                    ('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        """Removes select entry(ies)"""
        indices = self.querybox.curselection() # 0, 1, or more items
        for index in indices:
            self.querybox.delete(index)
            item = self.item_list[index] # need actual item to remove from dictionary
            self.item_list.remove[item]
            del self.item_dict[item]

    def onAdd(self):
        """Add queries"""
        window = Toplevel()
        QueryInfoFrame(window)

class QueryInfoFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.query_window = QueryWindow(self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Cancel', self.onClose, {'side':RIGHT}),
                        ('Submit', self.onSubmit, {'side':RIGHT}),
                        ('Add file', self.onAddFile, {'side':LEFT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        self.parent.destroy()

    def onSubmit(self):
        """Signals back to the main search widget to update listbox"""
        pass

    def onAddFile(self):
        """Adds a file and updates child widgets"""
        pass

class QueryWindow(ttk.Panedwindow):
    pass

class DatabaseFrame(Frame):
    def __init__(self, parent=None, text='Database', items=None):
        Frame.__init__(self, parent)
        self.dbbox = ScrollBoxFrame(self, text, items)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)
        self.buttons=[('Remove', self.onRemove, {'side':RIGHT}),
                    ('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        pass

    def onAdd(self):
        pass


