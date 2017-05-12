"""
This module contains code for a GUI frontend for searches
"""

import os
from tkinter import *
from tkinter import ttk, filedialog, messagebox

from gui.util import input_form
#from gui.database import database_gui

class SearchFrame(Frame):
    def __init__(self, db, search_obj, parent=None):
        Frame.__init__(self, parent)
        self.db = db
        self.search_obj = search_obj # keep a reference and pass it down
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        self.search = SearchGui(db, search_obj, self)
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
    def __init__(self, db, search_obj, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = ParamFrame(self)
        self.query_frame = QuerySummaryFrame(db,search_obj,self)
        self.db_frame = DatabaseSummaryFrame(self)
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
        self.algorithm = RadioBoxFrame(self, [('Blast','blast'), ('HMMer','hmmer')],
                labeltext='Algorithm')
        self.db_type = RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Target data type')
        self.keep_output = CheckBoxFrame(self, 'Keep output files?')

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.insert(0,dirpath)

class RadioBoxFrame(Frame):
    def __init__(self, parent=None, choices=None, labeltext=None):
        Frame.__init__(self, parent)
        self.choices = choices
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.selected = StringVar()
        for text,var in self.choices:
            ttk.Radiobutton(self, text=text, variable=self.selected,
                            value=var).pack(side=LEFT)
        self.selected.set(var) # set to last value

class CheckBoxFrame(Frame):
    def __init__(self, parent=None, labeltext=None):
        Frame.__init__(self, parent)
        self.pack()
        if labeltext:
            Label(self, text=labeltext).pack()
        self.checked = IntVar()
        self.checkbutton = ttk.Checkbutton(self, text='Yes',
                        variable=self.checked).pack()

class ScrollBoxFrame(Frame):
    def __init__(self, parent=None, text=None, items=None,
            other_widget=None, mode='extended'):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.other = other_widget
        if text:
            Label(self, text=text).pack(side=TOP)
        self.item_list = [] # internal list mapping to listbox list
        self.item_dict = {} # hashtable for listbox items
        self.listbox = Listbox(self, height=20, selectmode=mode)
        self.listbox.bind('<<ListboxSelect>>', self.onSelect)
        self.listbox.pack(side=LEFT)
        vs = ttk.Scrollbar(self, orient=VERTICAL, command=self.listbox.yview)
        vs.pack(side=RIGHT)
        self.listbox['yscrollcommand'] = vs.set
        if items:
            for item,value in items:
                self.listbox.insert('end', item)
                self.item_list.append(item)
                self.item_dict[item] = value

    def onSelect(self):
        pass # implement in other subclasses?

class QuerySummaryFrame(Frame):
    def __init__(self, db, search_obj, parent=None, text='Queries', items=None):
        Frame.__init__(self, parent)
        self.db = db
        self.search_obj = search_obj
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
        #QueryInfoFrame(self.db, window)
        QueryWindow(self.db, self.search_obj, window)

class QueryInfoFrame(Frame):
    def __init__(self, db, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.query_window = QueryWindow(db, self)
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
    def __init__(self, db, search_obj, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.db = db
        self.search_obj = search_obj
        self.parent = parent
        self.query_frame = QueryFrame(self, text='Queries', mode='browse',
                items=search_obj.queries)
        self.query_info = QueryInfoFrame(db, self)
        self.add(self.query_frame)
        self.add(self.query_info)
        self.pack(expand=YES, fill=BOTH)

    def update(self, item):
        """Called when a query is selected in the scrollbox. Updates the
        info frame to allow for modifications to query metadata"""
        self.query_info.update_name(item.identity)
        self.query_info.update_record(item.record)
        self.query_info.update_raccs(item.redundant_accs)

class QueryFrame(ScrollBoxFrame):
    """Inherit from Scrollbox but add handler for selection"""
    def onSelect(self):
        index = self.querybox.curselection() # guaranteed to be a single selection
        item = self.item_list[index] # need actual item
        self.other.update(item)

class QueryInfoFrame(Frame):
    def __init__(self, db, parent=None):
        Frame.__init__(self, parent)
        self.db = db
        self.pack()
        self.name = input_form.DefaultValueForm([('Name','')], self)
        # Deal with selecting records
        Label(self, text='Associated database record').pack(expand=YES, fill=X)
        self.selected_record = StringVar()
        self.record_box = ttk.Combobox(self, textvariable=self.selected_record)
        self.record_box['values'] = [self.db[x].identity for x in self.db.list_records()]
        self.record_box.pack(expand=YES, fill=X)
        # Deal with selecting data type
        self.db_type = RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Target data type')
        # Deal with redundant accessions
        Label(self, text='Associated redundant accessions').pack(expand=YES, fill=X)
        self.selected_racc = StringVar()
        self.racc_box = ttk.Combobox(self, textvariable=self.selected_racc)
        self.racc_box['values'] = [] # Need to change later to reflect raccs
        self.racc_box.pack(expand=YES, fill=X)
        Button(self, text='Add', command=self.onAdd).pack(side=RIGHT)

    def update_name(self, name):
        """Inserts name into form field"""
        self.name.row_list['Name'].entry.delete(0,'end') # clear first
        self.name.row_list['Name'].entry.insert(0,name) # then insert value

    def update_record(self, record):
        """Sets the value of the combobox"""
        self.selected_record.set(record)

    def update_raccs(self, *accs):
        """Updates racc box values to those of the chosen record"""
        self.racc_box['values'] = raccs[:]

    def onAdd(self):
        """Search against the database specified by chosen record and database
        type (e.g. genomic/protein) and allow user to choose"""
        target_db = self.db_type.selected.get() # e.g. 'protein'
        target_record = self.selected_record.get()
        if self.target_record == '': # user did not select
            pass # need to pop up a warning eventually
        name = self.name.row_list['Name'].entry.get()
        if name == '' or name is None:
            name = 'default'
        outpath = search_util.get_temporary_outpath(goat_dir, name)
        if target_db == 'protein':
            blast_search = blast_setup.BLASTp(blast_path, query, target_db, outpath)
        else:
            pass # implement for all types eventually
        blast_search.run_from_stdin()
        # need to add more code here to encompass manual vs auto selection

class DatabaseSummaryFrame(Frame):
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


