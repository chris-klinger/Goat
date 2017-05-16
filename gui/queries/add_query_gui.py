"""
This module contains code for adding queries in Goat.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util
from gui.queryes import query_gui

class AddQueryFrame(Frame):
    def __init__(self, other_widge=None, parent=None):
        Frame.__init__(self, parent)
        self.other_widget = other_widget
        self.layout = AddQueryGui(self)

        self.buttons = [('Add by File', self.onAddFile, {'side':LEFT}),
                        ('Add manually', self.onAddMan, {'side':LEFT}),
                        ('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onAddFile(self):
        """Prompts user to add a file and associated data"""
        window = Toplevel()
        AddFileFrame(window)

    def onAddMan(self):
        """Prompts user to add a single query and associated data"""
        window = Toplevel()
        AddManualFrame(window)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        pass

    def onCancel(self):
        """Closes the window without actually adding queries"""
        pass

class AddQueryGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.query_list = QueryListFrame()
        self.info_frame = QueryInfoFrame()
        self.added_list = AddedListFrame()
        self.add(self.query_list)
        self.add(self.info_frame)
        self.add(self.added_list)

class QueryListFrame(gui_util.ScrollBoxFrame):
    def __init__(self, parent, text, other_widget):
        gui_util.ScrollBoxFrame.__init__(self, parent, text,
                other_widget=other_widget)

        self.toolbar = Frame(self)
        self.buttons = [('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSelect(self):
        """Display information in parent middle widget"""
        pass

    def onAdd(self):
        """Adds selected entry(ies) to added widget"""
        pass

class QueryInfoFrame(query_gui.QueryInfoFrame):
    def __init__(self, record_db, parent=None):
        query_gui.QueryInfoFrame.__init__(self, record_db, parent)

    # may want to override one or both methods
    def onRemove(self):
        """Remove from both associated widgets?"""
        pass

    def onModify(self):
        """For RAccs, keep the same as in query gui?"""
        pass

class AddedListFrame(gui_util.ScrollBoxFrame):
    def __init__(self, parent, text, other_widget):
        gui_util.ScrollBoxFrame.__init__(self, parent, text,
                other_widget=other_widget)

        self.toolbar = Frame(self)
        self.buttons = [('Remove', self.onRemove, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSelect(self):
        """Display information in parent middle widget"""
        pass

    def onRemove(self):
        """Removes selected entry(ies) from own display"""
        pass

class AddFileFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        pass

class AddManualFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        pass
