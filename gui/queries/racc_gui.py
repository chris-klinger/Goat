"""
This module contains code for choosing redundant accessions to associated with a query.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util

class AddRaccFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.layout = AddRaccGui(self)
        self.pack(expand=YES, fill=BOTH)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        pass

    def onCancel(self):
        """Closes the window without actually modifying raccs"""
        pass

class AddRaccGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.pack(expand=YES, fill=BOTH)
        self.blast_list = BlastListFrame(self, 'BLAST Hits')
        self.added_list = AddedListFrame(self, 'To be Added')
        self.add(self.blast_list)
        self.add(self.added_list)
        # to avoid AttributeError, link widgets after each is assigned
        self.blast_list.link_widget(self.added_list)
        self.added_list.link_widget(self.query_list)

class BlastListFrame(Frame):
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


