"""
This module contains code for choosing redundant accessions to associated with a query.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util, input_form

class AddRaccFrame(Frame):
    def __init__(self, query, query_db, record_db, parent=None):
        Frame.__init__(self, parent)
        self.qobj = query
        self.qdb = query_db
        self.parent = parent
        self.layout = AddRaccGui(query, record_db, self)
        self.pack(expand=YES, fill=BOTH)

        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        new_attrs = {}
        info = self.layout.query_info
        for row in info.name.row_list: # can we get without for-loop?
            if row.label_text == 'Name':
                new_attrs['name'] = row.entry.get()
        new_attrs['search_type'] = info.qtype.selected.get()
        new_attrs['db_type'] = info.alphabet.selected.get()
        new_attrs['record'] = info.record.selected.get()
        for attr,value in new_attrs.items():
            setattr(self.qobj,attr,value) # change values, or reset unchanged ones
        self.qobj.modify_raccs(*self.layout.added_list.lbox_frame.item_list)
        self.qdb.add_query(self.qobj.identity,self.qobj) # adding back same as modifying
        self.parent.destroy()

    def onCancel(self):
        """Closes the window without actually modifying raccs"""
        self.parent.destroy()

class AddRaccGui(ttk.Panedwindow):
    def __init__(self, query, record_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.qobj = query
        self.pack(expand=YES, fill=BOTH)
        self.query_info = QueryInfoFrame(record_db, self)
        self.blast_list = BlastListFrame(self, 'BLAST Hits')
        self.added_list = AddedListFrame(self, 'To be Added')
        self.add(self.query_info)
        self.add(self.blast_list)
        self.add(self.added_list)
        # to avoid AttributeError, link widgets after each is assigned
        self.blast_list.link_widget(self.added_list)
        self.added_list.link_widget(self.blast_list)
        # set windows to current state of selected query
        self.populate_windows()

    def populate_windows(self):
        """Retrieves information from the passed in query and changes the child
        display windows to display this information"""
        for row in self.query_info.name.row_list:
            if row.label_text == 'Name':
                row.entry.insert(0,self.qobj.name) # insert name
        self.query_info.qtype.selected.set(self.qobj.search_type) # select search type
        self.query_info.alphabet.selected.set(self.qobj.db_type) # select db type
        self.query_info.record.selected.set(self.qobj.record) # select record
        # Now populate both racc windows
        all_accs = []
        raccs = []
        for title,evalue in self.qobj.all_accs: # list of lists
            display_string = str(title) + '  ' + str(evalue)
            all_accs.append([display_string,(title,evalue)])
        if not len(self.qobj.redundant_accs) == 0: # there are hits
            for item in self.qobj.redundant_accs:
                print(item)
            #for title,evalue in self.qobj.redundant_accs: # already a list
                #display_string = str(title) + '  ' + str(evalue)
                #raccs.append([display_string,(title,evalue)])
        self.blast_list.lbox_frame.add_items(all_accs)
        self.added_list.lbox_frame.add_items(raccs)

class QueryInfoFrame(Frame):
    def __init__(self, record_db, parent=None):
        Frame.__init__(self, parent)
        self.rdb = record_db
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Query Information').pack(expand=YES, fill=X, side=TOP)
        self.name = input_form.DefaultValueForm([('Name','')],self)
        self.qtype = gui_util.RadioBoxFrame(self, [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self, [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self, self.rdb.list_entries(), # record db keys
                labeltext='Associated record')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

class BlastListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', self.onAdd)

        self.toolbar = Frame(self)
        self.toolbar.pack(expand=YES, fill=X, side=BOTTOM)
        self.buttons = [('Add', self.onAdd, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

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
            ttk.Button(self.toolbar, text=label, command=action).pack(where)

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


