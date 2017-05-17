"""
This module contains code for adding queries in Goat.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util, input_form

class AddQueryFrame(Frame):
    def __init__(self, record_db, parent=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self.parent = parent
        self.layout = AddQueryGui(self)
        self.pack(expand=YES, fill=BOTH)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Add by File', self.onAddFile, {'side':LEFT}),
                        ('Add manually', self.onAddMan, {'side':LEFT}),
                        ('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onAddFile(self):
        """Prompts user to add a file and associated data"""
        window = Toplevel()
        AddFileFrame(self.rdb, window)

    def onAddMan(self):
        """Prompts user to add a single query and associated data"""
        window = Toplevel()
        AddManualFrame(self.rdb, window)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        pass

    def onCancel(self):
        """Closes the window without actually adding queries"""
        pass

class AddQueryGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.pack(expand=YES, fill=BOTH)
        self.query_list = QueryListFrame(self, 'Possible Queries')
        self.added_list = AddedListFrame(self, 'To be Added')
        self.add(self.query_list)
        self.add(self.added_list)
        # to avoid AttributeError, link widgets after each is assigned
        self.query_list.link_widget(self.added_list)
        self.added_list.link_widget(self.query_list)

class QueryListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', self.onAdd)

        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, fill=X, side=BOTTOM)
        self.buttons = [('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def link_widget(self, widget):
        """Hook up another widget after instantiation"""
        self.other = widget

    def onAdd(self):
        """Adds selected entry(ies) to added widget"""
        selected = self.lbox_frame.listbox.curselection()
        self.other.lbox_frame.add_items([self.listbox.get(index) for index in selected])
        self.lbox_frame.remove_items(*selected)

class AddedListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', self.onRemove)

        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, fill=X, side=BOTTOM)
        self.buttons = [('Remove', self.onRemove, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def link_widget(self, widget):
        """Hook up another widget after instantiation"""
        self.other = widget

    def onRemove(self):
        """Removes selected entry(ies) from own display"""
        selected = self.lbox_frame.listbox.curselection()
        self.other.lbox_frame.add_items([self.listbox.get(index) for index in selected])
        self.lbox_frame.remove_items(*selected)

class AddFileFrame(Frame):
    def __init__(self, record_db, parent=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='File Information').pack(expand=YES, fill=X, side=TOP)
        self.cfile = input_form.FileValueForm(self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self, self.rdb.list_records(), # record db keys
                labeltext='Associated record')
        self.add_raccs = gui_util.RadioBoxFrame(self, [('No','no'), ('Auto','auto'),
            ('Manual','man')], labeltext='Add Redundant Accessions?')

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Signals back to other widget to update queries"""
        pass

    def onCancel(self):
        """Closes the window without actually adding queries"""
        self.parent.destroy()

class AddManualFrame(Frame):
    def __init__(self, record_db, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.layout = AddManualGui(record_db, self)
        self.pack(expand=YES, fill=BOTH)

        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, fill=X, side=BOTTOM)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Signals back to other widget to update queries"""
        pass

    def onCancel(self):
        """Closes the window without actually adding queries"""
        self.parent.destroy()

class AddManualGui(ttk.Panedwindow):
    def __init__(self, record_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.seq_entry = SeqEntryFrame(self)
        self.seq_info = SeqInfoFrame(record_db, self)
        self.add(self.seq_entry)
        self.add(self.seq_info)
        self.pack(expand=YES, fill=BOTH)

class SeqEntryFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Input Sequence').pack(expand=YES, fill=X, side=TOP)
        # will eventually need to implement a much more complex interface
        # for the canvas, and add scrollbars, etc.
        self.entry = Canvas(width=200, height=400, bg='white')

class SeqInfoFrame(Frame):
    def __init__(self, record_db, parent=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Sequence Information').pack(expand=YES, fill=X, side=TOP)
        self.name = input_form.DefaultValueForm([('Name','')],self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self, self.rdb.list_records(), # record db keys
                labeltext='Associated record')
        self.add_raccs = gui_util.RadioBoxFrame(self, [('No','no'), ('Auto','auto'),
            ('Manual','man')], labeltext='Add Redundant Accessions?')

