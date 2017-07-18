"""
This module contains code to add/modify query sets. Idea is to have the same
interface for adding/modifying, as the only required information is to have
the set name and the queries to include in the set
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util, input_form

class QuerySetFrame(Frame):
    def __init__(self, query_db, parent=None, qset=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.qset = qset # This should be a dictionary key!!!
        self.parent = parent
        Label(self, text='Query Set Information').pack(expand=YES, fill=X, side=TOP)
        if self.qset: # not None
            self.name = input_form.DefaultValueForm(
                    [('Set Name',str(self.name))],self) # insert set name already
        else:
            self.name = input_form.DefaultValueForm(
                    [('Set Name','')],self) # blank value to fill in
        self.set_gui = SetGui(query_db, self.qset, self)
        self.pack(expand=YES, fill=BOTH)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Submit', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Adds or modifies a query set; signals back to tree widget to
        redraw itself"""
        pass

    def onCancel(self):
        """Closes without adding/modifying any sets"""
        pass

class SetGui(ttk.Panedwindow):
    def __init__(self, query_db, qset, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.qdb = query_db
        self.qset = qset
        self.pack(expand=YES, fill=BOTH)
        self.set_list = SetListFrame(self, 'Possible Queries')
        self.added_list = AddedListFrame(self, 'Queries in Set')
        self.add(self.set_list)
        self.add(self.added_list)
        # Link widgets to allow communication
        self.set_list.link_widget(self.added_list)
        self.added_list.link_widget(self.set_list)
        # Set windows to current state of selected query
        self.populate_windows()

    def populate_windows(self):
        """Retrieves information from query DB regarding both set and queries to
        populate both windows"""
        if not self.qset: # i.e. it is still NoneType; adding a new set
            self.set_list.lbox_frame.add_items(
                    [(item,'') for item in self.qdb.list_queries()]) # add all queries
        else:
            self.set_list.lbox_frame.add_items([(item,'') for item in self.qdb.list_queries()
                if not item in self.qdb.sets.qdict[self.qset]]) # add if not already present
            self.added_list.lbox_frame.add_items([self.qdb.sets.qdict[self.qset]])

class SetListFrame(Frame):
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
        items = [self.lbox_frame.listbox.get(index) for index in selected]
        to_add = []
        for item,index in zip(items,selected):
            value = self.lbox_frame.item_dict[item]
            to_add.append([item, value, index])
        self.other.lbox_frame.add_items(to_add, 'index')
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
        items = [self.lbox_frame.listbox.get(index) for index in selected]
        to_remove = []
        for item,index in zip(items,selected):
            value = self.lbox_frame.item_dict[item]
            to_remove.append([item, value, index])
        self.other.lbox_frame.add_items(to_remove, 'index')
        self.lbox_frame.remove_items(*selected)

