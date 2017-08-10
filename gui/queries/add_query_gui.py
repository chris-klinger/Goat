"""
This module contains code for adding queries in Goat.
"""

from tkinter import *
from tkinter import ttk
#import _thread

from queries import query_file
from gui.util import gui_util, input_form
#from gui.searches import threaded_search # return to this later

class AddQueryFrame(Frame):
    def __init__(self, query_db, record_db, query_widget, parent=None):
        Frame.__init__(self, parent)
        self.qdb = query_db
        self.rdb = record_db
        self.qwidget = query_widget
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
        AddFileFrame(self.rdb, self.layout, window)

    def onAddMan(self):
        """Prompts user to add a single query and associated data"""
        window = Toplevel()
        AddManualFrame(self.rdb, window)

    def onSubmit(self):
        """Submits the request; all added queries are added to the DB and
        committed, and the window is closed"""
        to_add = self.layout.added_list.lbox_frame.item_dict # dictionary
        #print(to_add)
        qlist = []
        qwidget_lbox = self.qwidget.query.query_frame.query_notebook.qlist # super gross...
        for k,v in to_add.items():
            self.qdb.add_query(k, v) # add to database - by object now
            qlist.append([k,v])
        qwidget_lbox.add_items(qlist) # add to display
        self.parent.destroy()

    def onCancel(self):
        """Closes the window without actually adding queries"""
        self.parent.destroy()

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
        items = [self.lbox_frame.listbox.get(index) for index in selected] # get associated items
        to_add = []
        for item in items: # step through items
            value = self.lbox_frame.item_dict[item] # fetch associated value
            to_add.append([item, value]) # build dictionary
        self.other.lbox_frame.add_items(to_add) # add as dictionary
        self.lbox_frame.remove_items(*selected) # also removes from internal list and dict

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
        """Removes selected entry(ies) from own display
        Same as QueryListFrame onAdd function but in reverse"""
        selected = self.lbox_frame.listbox.curselection()
        items = [self.lbox_frame.listbox.get(index) for index in selected]
        to_remove = []
        for item in items:
            value = self.lbox_frame.item_dict[item]
            to_remove.append([item, value])
        self.other.lbox_frame.add_items(to_remove)
        self.lbox_frame.remove_items(*selected)

def update_listbox(listbox, item_list):
    """Actually updates the listbox"""
    listbox.lbox_frame.add_items(item_list) # add to display

class AddFileFrame(Frame):
    def __init__(self, record_db, layout, parent=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self._owidget = layout
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='File Information').pack(expand=YES, fill=X, side=TOP)
        self.cfile = input_form.FileValueForm(self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'),
            ('Genomic','genomic')], labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self,
                list(self.rdb.list_entries()), # record db keys; use list function or returns a generator
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
        qtype = self.qtype.selected.get()
        if qtype == 'seq':
            queries = query_file.FastaFile(self.cfile.content['Filename'].get(),
                qtype, self.alphabet.selected.get(), self.record.selected.get(),
                self.add_raccs.selected.get()).get_queries()
            if self.add_raccs.selected.get() != 'no': # we want to add raccs
                if self.record.selected.get() == '': # but there is not associated record!
                    raise AttributeError
                for v in queries:
                    v.run_self_blast(self.rdb)
                update_listbox(self._owidget.query_list, queries)
            else: # no need to run searches
                update_listbox(self._owidget.query_list, queries)
        elif qtype == 'hmm':
            queries = query_file.HMMFile(self.cfile.content['Filename'].get(),
                qtype, self.alphabet.selected.get(), self.record.selected.get(),
                self.add_raccs.selected.get()).get_query()
            update_listbox(self._owidget.query_list, queries)
        self.parent.destroy()

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
        try:
            info_frame = self.layout.seq_info
            if info_frame.add_raccs != 'no': # we want to add raccs
                if not info_frame.record: # but there is not associated record!
                    raise AttributeError
            #self.parent.
            info = self.layout.seq_info
            qid = info.names.content['Identity'].get()
            qobj = query_obj.Query(qid, info.names.content['Name'].get(),
                info.names.content['Description'].get(), '', info.qtype.get(),
                info.alphabet.get(), self.seq_entry.entry.get(),
                record=info.record.get(), self_blast=info.add_raccs.get())
            self.parent.query_list.lbox_frame.add_items(qid)
            self.parent.query_list.queries[qid] = qobj
        except(AttributeError):
            # do not allow raccs if no record specified
            messagebox.showwarning('Incompatible options',
                'Cannot choose to add redundant accessions without associated record')

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
        self.names = input_form.DefaultValueForm([('Identity',''),('Name',''),
            ('Description','')],self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self, self.rdb.list_entries(), # record db keys
                labeltext='Associated record')
        self.add_raccs = gui_util.RadioBoxFrame(self, [('No','no'), ('Auto','auto'),
            ('Manual','man')], labeltext='Add Redundant Accessions?')

