"""
This module contains code for a GUI frontend for searches
"""

import os
from tkinter import *
from tkinter import ttk, filedialog #, messagebox

from bin.initialize_goat import configs

from searches import search_obj, search_runner
from results import intermediate
from gui.util import input_form, gui_util
#from gui.database import database_gui

class SearchFrame(Frame):
    def __init__(self, parent=None): #query_db, record_db, search_db, result_db, parent=None):
        Frame.__init__(self, parent)
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']
        self.sdb = configs['search_db']
        self.udb = configs['result_db']
        self._dbs = [self.qdb, self.rdb, self.sdb, self.udb]

        self.pack(expand=YES, fill=BOTH)
        #self.search = SearchGui(query_db, record_db, self)
        self.search = SearchGui(self.qdb, self.rdb, self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Cancel', self.onClose, {'side':RIGHT}),
                        ('Run', self.onRun, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close without actually running the search"""
        self.parent.destroy()

    def onRun(self):
        """Runs the search and populates the necessary files/databases"""
        params = self.search.param_frame
        queries = self.search.query_frame.querybox
        dbs = self.search.db_frame.db_box
        for row in params.entries.row_list:
            if row.label_text == 'Name':
                sname = row.entry.get()
            elif row.label_text == 'Location':
                location = row.entry.get()
        if params.keep_output.checked.get() == 0:
            ko = False
        else:
            ko = True
        sobj = search_obj.Search( # be explicit for clarity here
            name = sname,
            algorithm = params.algorithm.selected.get(),
            q_type = params.q_type.selected.get(),
            db_type = params.db_type.selected.get(),
            queries = queries.item_list, # equivalent to all queries
            databases = dbs.item_list, # equivalent to all dbs
            keep_output = ko,
            output_location = location)
        # store search object in database
        #self.sdb[sname] = sobj # should eventually make a check that we did actually select something!
        # now run the search and parse the output
        #runner = search_runner.SearchRunner(sobj, self.qdb, self.rdb, self.udb)
        runner = search_runner.SearchRunner(name, sobj, self.qdb, self.rdb, self.udb, self.sdb,
                threaded=False, gui=self)
        print("calling threaded runner.run() from forward search")
        runner.run()
        # Can destroy once run starts
        print("calling runner.parse() from forward search")
        runner.parse()
        print("calling self.onSaveQuit() from forward search")
        self.onClose()

class SearchGui(ttk.Panedwindow):
    def __init__(self, query_db, record_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = ParamFrame(self)
        self.query_frame = QuerySummaryFrame(query_db, self)
        self.db_frame = DatabaseSummaryFrame(record_db, self)
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
        self.algorithm = gui_util.RadioBoxFrame(self, [('Blast','blast'), ('HMMer','hmmer')],
                labeltext='Algorithm')
        self.q_type = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Query data type')
        self.db_type = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Target data type')
        self.keep_output = gui_util.CheckBoxFrame(self, 'Keep output files?')

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

class QuerySummaryFrame(Frame):
    def __init__(self, query_db, parent=None, text='Queries', items=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.querybox = gui_util.ScrollBoxFrame(self, text, items)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)
        self.buttons=[('Remove Query(ies)', self.onRemove, {'side':RIGHT}),
                    ('Add Query(ies)', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        """Removes select entry(ies)"""
        selected = self.querybox.listbox.curselection() # 0, 1, or more items
        self.querybox.remove_items(*selected) # object itself handles removal

    def onAdd(self):
        """Add queries"""
        window = Toplevel()
        QueryWindow(self.qdb, self, window)

class QueryWindow(Frame):
    def __init__(self, query_db, other_widget, parent=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.owidget = other_widget # ref to send back updates
        self.parent = parent
        Label(self, text='Available Queries').pack(expand=YES, fill=X, side=TOP)
        self.notebook = QuerySearchNotebook(query_db, self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.pack(expand=YES, fill=BOTH)

        self.buttons = [('Submit', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Checks whether the treeview or list widget is in focus, then checks the
        selection in the relevant widget. Adds (query_id/query_value) pairs to a
        list, checking for duplicates. If the treeview widget is selected, query
        objects are retrieved from the database. Finally, adds selected query(ies)
        to the listbox in the main window, again skipping duplicates"""
        notebook = self.notebook
        to_add = [] # common list to add to main widget from
        if notebook.select() == str(notebook.qset):
            seen = set() # must account for possible multiple instances
            for item_name in notebook.qset.selection(): # one or more items, unlike focus
                item = notebook.qset.item(item_name)
                if item['tags'][0] == 'query': # simple case
                    if not item_name in seen:
                        to_add.append([item_name,'']) # '' because need a value as well
                        seen.add(item_name)
                else: # set
                    set_list = self.qdb.sets.qdict[item_name]
                    for qid in set_list:
                        if qid not in seen:
                            to_add.append([qid,''])
                            seen.add(qid)
        elif notebook.select() == str(notebook.qlist):
            selected = notebook.qlist.listbox.curselection()
            if len(selected) > 0:
                # no chance for duplicate entries, '' is the 'value'
                to_add.extend([(notebook.qlist.listbox.get(index),'') for index in selected])
        # now try adding
        if len(to_add) > 0:
            self.owidget.querybox.add_items(to_add)
        self.parent.destroy() # either way, close window

    def onCancel(self):
        """Quits without adding any queries"""
        self.parent.destroy()

class QuerySearchNotebook(ttk.Notebook):
    def __init__(self, query_db, parent=None):
        ttk.Notebook.__init__(self, parent)
        self.qset = QSearchSetViewer(query_db, self)
        self.qlist = QSearchListViewer(query_db, self)
        self.add(self.qset, text='Query Sets')
        self.add(self.qlist, text='All Queries')
        self.pack(expand=YES, fill=BOTH)

class QSearchSetViewer(ttk.Treeview):
    def __init__(self, query_db, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.qdb = query_db
        self.config(selectmode='extended') # want multiple selection here
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def make_tree(self):
        """Builds a treeview display of sets/queries"""
        for key in self.qdb.sets.list_query_sets():
            if key == '_ALL':
                self.insert('','end',key,text='All queries',tags=('set'))
            else:
                self.insert('','end',key,text=key,tags=('set'))
            for qid in self.qdb.sets.qdict[key]: # iterate over list of qids
                self.insert(key,'end',qid,text=qid,tags=('query'))

class QSearchListViewer(gui_util.ScrollBoxFrame):
    def __init__(self, query_db, parent=None):
        to_display = [] # init with queries in db
        for key in query_db.list_queries():
            to_display.append([key,'']) # here, '' is 'value' as we don't need the obj
        gui_util.ScrollBoxFrame.__init__(self, parent, items=to_display)
        self.qdb = query_db

class DatabaseSummaryFrame(Frame):
    def __init__(self, record_db, parent=None, text='Database', items=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self.db_box = gui_util.ScrollBoxFrame(self, text, items)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)
        self.buttons=[('Remove Database(s)', self.onRemove, {'side':RIGHT}),
                    ('Add Database(s)', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRemove(self):
        """Removes select entry(ies)"""
        selected = self.db_box.listbox.curselection()
        self.db_box.remove_items(*selected)

    def onAdd(self):
        """Adds databases"""
        window = Toplevel()
        DatabaseWindow(self.rdb, self, window)

class DatabaseWindow(Frame):
    def __init__(self, record_db, other_widget, parent=None):
        Frame.__init__(self, parent)
        self.owidget = other_widget # ref to send back updates
        self.parent = parent
        Label(self, text='Available Databases').pack(expand=YES, fill=X, side=TOP)
        self.rlist = gui_util.ScrollBoxFrame(self,
                items=[(key,'') for key in record_db.list_records()],
                mode='multiple')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.pack(expand=YES, fill=BOTH)

        self.buttons = [('Submit', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Adds selected records to the database list in parent widget"""
        to_add = []
        selected = self.rlist.listbox.curselection()
        if len(selected) > 0:
            # '' because requires a value as well
            to_add.extend([(self.rlist.listbox.get(index),'') for index in selected])
            self.owidget.db_box.add_items(to_add)
        self.parent.destroy()

    def onCancel(self):
        """Quits without adding any records"""
        self.parent.destroy()

##########################################
# Interface for running reverse searches #
##########################################

class ReverseSearchFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']
        self.sdb = configs['search_db']
        self.udb = configs['result_db']
        self._dbs = [self.qdb, self.rdb, self.sdb, self.udb]

        self.search_name = gui_util.ComboBoxFrame(self,
            choices = list(self.sdb.list_entries()),
            labeltext = 'Forward search to use')
        self.params = ReverseParamFrame(self)
        self.pack(expand=YES,fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Cancel', self.onClose, {'side':RIGHT}),
                        ('Run', self.onRun, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close without actually running the search"""
        self.parent.destroy()

    def onSaveQuit(self):
        """Commits changes to dbs after a search"""
        for db in self._dbs:
            db.commit()
        self.onClose()

    def onRun(self):
        """Runs the search and populates the necessary files/databases"""
        fwd_search = self.search_name.selected.get()
        fwd_sobj = self.sdb[fwd_search]
        # Next function call adds search result queries to query database
        intermediate.Search2Queries(
            fwd_sobj, self.udb, self.qdb, self.rdb).populate_search_queries()
        # Now get all needed queries
        queries = []
        for uid in fwd_sobj.list_results(): # result ids
            #print(uid)
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                #print('\t' + str(qid))
                queries.append(qid)
        params = self.params
        for row in params.entries.row_list:
            if row.label_text == 'Name':
                sname = row.entry.get()
            elif row.label_text == 'Location':
                location = row.entry.get()
        if params.keep_output.checked.get() == 0:
            ko = False
        else:
            ko = True
        rev_sobj = search_obj.Search( # be explicit for clarity here
            name = sname,
            algorithm = params.algorithm.selected.get(),
            q_type = fwd_sobj.db_type, # queries here are the same as the forward db type
            db_type = fwd_sobj.q_type, # conversely, db is the original query type
            queries = queries, # equivalent to all queries
            databases = [], # reverse search, so target_db is on each query!
            keep_output = ko,
            output_location = location)
        # store search object in database
        #self.sdb[sname] = rev_sobj # should eventually make a check that we did actually select something!
        # now run the search and parse the output
        #runner = search_runner.SearchRunner(rev_sobj, self.qdb, self.rdb, self.udb,
                #mode='old', fwd_search=fwd_sobj)
        #print("calling runner.run() from reverse search")
        #runner.run()
        runner = search_runner.SearchRunner(name, rev_sobj, self.qdb, self.rdb, self.udb, self.sdb,
                mode='old', fwd_search=fwd_sobj, threaded=True, gui=self)
        print("calling threaded runner.run() from reverse search")
        runner.run()
        #print("calling runner.parse() from reverse search")
        #runner.parse()
        #print("calling self.onSaveQuit() from reverse search")
        #self.onSaveQuit()

class ReverseParamFrame(Frame):
    """Like ParamFrame, but without query and db type options"""
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        self.curdir = os.getcwd()
        self.entries = input_form.DefaultValueForm([('Name',''), ('Location',self.curdir)],
                self, [('Choose Directory', self.onChoose, {'side':RIGHT})])
        self.algorithm = gui_util.RadioBoxFrame(self, [('Blast','blast'), ('HMMer','hmmer')],
                labeltext='Algorithm')
        self.keep_output = gui_util.CheckBoxFrame(self, 'Keep output files?')

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

