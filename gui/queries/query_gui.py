"""
This module contains code for dealing with viewing and updating queries
"""

from tkinter import *
from tkinter import ttk, messagebox

from gui.queries import add_query_gui, racc_gui
#from gui.util import input_form
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
                        ('Modify Query', self.onModify, {'side':LEFT}),
                        ('Remove', self.onRemove, {'side':LEFT}),
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
        window = Toplevel()
        add_query_gui.AddQueryFrame(self.qdb, self.rdb, self, window)

    def onModify(self):
        """Checks whether a single query is selected in either window. Assuming
        yes, pops up a new window to modify the selection"""
        notebook = self.query.query_frame.query_notebook
        if notebook.select() == str(notebook.qset): # select() returns string, must convert
            pass # tree is selected, do something
        elif notebook.select() == str(notebook.qlist):
            selected = notebook.qlist.listbox.curselection()
            slen = len(selected)
            if slen == 1: # exactly one item selected
                item = notebook.qlist.listbox.get(selected) # query id
                qobj = notebook.qlist.item_dict[item] # get actual object
                window = Toplevel()
                racc_gui.AddRaccFrame(qobj, self.qdb, self.rdb, window) # now modify

    def onRemove(self):
        """Checks whether one or more queries is selected in either window (i.e.
        without any sets selected as well; Asks for confirmation about removal
        and then removes those queries from the DB"""
        notebook = self.query.query_frame.query_notebook
        if notebook.select() == str(notebook.qset): # select() returns string, must convert
            pass # tree is selected, do something
        elif notebook.select() == str(notebook.qlist):
            selected = notebook.qlist.listbox.curselection()
            slen = len(selected)
            if slen > 0:
                items = [notebook.qlist.listbox.get(index) for index in selected]
                if messagebox.askyesno(
                    message = "Delete {} queries?".format(slen),
                    icon='question', title='Remove query(ies)'):
                    for query_id in items: # items holds a reference
                        self.qdb.remove_query(query_id)
                    notebook.qlist.remove_items(*selected) # remove from listbox
                    # also need to remove from tree eventually!!!

    def onSave(self):
        """Signals to associated dbs to commit but not close"""
        pass

    def onCancel(self):
        """Closes database connections but does not commit unsaved changes"""
        self.onClose()

    def onSubmit(self):
        """Commits and closes associated databases"""
        pass

class QueryGui(ttk.Panedwindow):
    def __init__(self, query_db, record_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        #self.info_frame = QueryInfoFrame(record_db, self)
        self.info_frame = QueryInfo(self)
        self.query_frame = QueryListFrame(query_db, self.info_frame, self)
        self.add(self.query_frame)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

class QueryListFrame(Frame):
    def __init__(self, query_db, info_widget, parent=None):
        Frame.__init__(self, parent)
        Label(self, text='Available Queries').pack(expand=YES, fill=X, side=TOP)
        self.query_notebook = QueryNotebook(query_db, info_widget, self)
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
    def __init__(self, query_db, info_widget, parent=None):
        ttk.Notebook.__init__(self, parent)
        self.qset = QuerySetViewer(query_db, self)
        self.qlist = QueryScrollBox(query_db, info_widget, self)
        self.add(self.qset, text='Query Sets')
        self.add(self.qlist, text='All Queries')
        self.pack(expand=YES, fill=BOTH)

class QuerySetViewer(ttk.Treeview):
    def __init__(self, query_db, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)

class QueryScrollBox(gui_util.ScrollBoxFrame):#Listbox):
    def __init__(self, query_db, other_widget, parent=None):
        to_display = []
        for key in query_db.list_queries():
            #print("fetching queries")
            #print(key)
            value = query_db[key]
            to_display.append([key,value])
        gui_util.ScrollBoxFrame.__init__(self, parent, items=to_display, # display any known queries to start
                other_widget=other_widget) # owidg is info frame
        self.qdb = query_db

    def onSelect(self, *args):
        """If only one item is selected, need to display info for query object
        in info panel; if more than one item is selected, do nothing"""
        selected = self.listbox.curselection()
        if len(selected) > 1: # cannot display information for more than one
            pass # do nothing
        else:
            to_display = []
            item = self.listbox.get(selected) # selected is the index
            qobj = self.qdb[item]
            to_display.extend([qobj.identity, qobj.name, qobj.search_type,
                qobj.db_type, qobj.record])
            if len(qobj.redundant_accs) != 0: # i.e., there are some to display
                for racc in qobj.redundant_accs:
                    to_display.append(racc)
            #print(to_display)
            self.other.update_info('query', *to_display)

class QueryInfo(ttk.Label):
    def __init__(self, parent=None):
        ttk.Label.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.displayInfo = StringVar() # re-displays on update
        self.config(textvariable = self.displayInfo,
                width=-75, # set wide to accommodate raccs?
                anchor='center',justify='center')
        self.displayInfo.set('') # initialize to empty value

    def update_info(self, display_type, *values):
        """Takes a list of values and displays it depending on whether the item
        clicked represents a single record or a single set. Calling function has
        responsibility to disregard multiple selections for display"""
        display_string = ''
        if display_type == 'set':
            display_string += ('Query Set Information: \n\n\n')
            display_string += ('Number of queries: ' + values[0] + '\n')
            # more information to display for sets here?
        elif display_type == 'query':
            display_string += ('Query Information: \n\n\n')
            display_string += ('Query Identity: ' + values[0] + '\n')
            display_string += ('Query Name: ' + values[1] + '\n')
            display_string += ('Query Type: ' + values[2] + '\n') # e.g. Seq or HMM
            display_string += ('Query Alphabet: ' + values[3] + '\n') # e.g. protein
            display_string += ('Query Record: ' + values[4] + '\n')
            if len(display_string) > 5: # redundant accessions present
                display_string += ('Redundant Accessions: ' + '\n')
                for value in values[5:]: # remaining args
                    display_string += ('  ' + value + '\n')
        self.displayInfo.set(display_string)

