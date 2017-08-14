"""
This module contains updated code for interacting with queries only, without
worrying about sets. Idea here is to separate queries by their type and provide
separate windows to interact with different types of queries for modifying/
adding them to the underlying database.
"""

import string,random
from tkinter import *
from tkinter import ttk, messagebox

from bin.initialize_goat import configs

from gui.util import gui_util, input_form
from queries import query_file
from searches import search_obj, search_util
from gui.searches import new_threaded_search

class QueryFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.qdb = configs['query_db']
        self.mqdb = configs['misc_queries']
        self.qsdb = configs['query_sets']
        self.pack(expand=YES, fill=BOTH)
        self.paned_window = SplitQueryWindow(self)
        # Add the toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Add Query(ies)', self.onAdd, {'side': LEFT}),
                        ('Modify Query', self.onModify, {'side': LEFT}),
                        ('Remove Query(ies)', self.onRemove, {'side': LEFT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        self.qdb.commit()
        self.mqdb.commit()
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

    def onAdd(self):
        """
        Determines which window is selected in the associated notebook widget and
        then provide an interface to add queries of the selected type.
        """
        qtype = self.paned_window.notebook_tab()
        window = Toplevel()
        AddQueryFrame(window, self, qtype)

    def add_queries(self, qlist):
        """
        Called from onAdd frame once queries are ready to submit. List has key,
        value pairs to add to the scrollbox.
        """
        self.paned_window.add_items(qlist)

    def onModify(self):
        """
        Determines which window is selected in the associated notebook widget and
        then provide an interface to add queries of the selected type.
        """
        to_mod = self.paned_window.notebook_selection()
        if len(to_mod) == 1: # exactly one item selected
            item = self.paned_window.notebook_item(to_mod)
            qobj = self.qdb[item]
            window = Toplevel()
            if qobj.search_type == 'seq':
                ModifySeqQuery(window, qobj)
            elif qobj.search_type == 'hmm':
                ModifyHMMQuery(window, qobj)
            else:
                ModifyMSAQuery(window, qobj)

    def onRemove(self):
        """
        Checks whether one or more queries is selected, and then asks for
        confirmation before removing them from the database.
        """
        to_remove = self.paned_window.notebook_selection() # returns indices
        #print(to_remove)
        rlen = len(to_remove)
        remove = False
        if rlen == 1:
            if messagebox.askyesno(
                    message = "Delete {} query?".format(rlen),
                    icon='question', title='Remove query'):
                remove = True
        elif rlen > 1:
            if messagebox.askyesno(
                    message = "Delete {} queries?".format(rlen),
                    icon='question', title='Remove queries'):
                remove = True
        if remove:
            for index in to_remove:
                qid = self.paned_window.notebook_item(index)
                self.qdb.remove_entry(qid)
                self.qsdb.remove_from_all(qid)
            # remove from listbox and internal data structures
            self.paned_window.remove_items(to_remove)

class SplitQueryWindow(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.info_frame = QueryInfo(self)
        self.notebook = QueryNotebook(self, self.info_frame) # link widget to display info
        self.add(self.notebook)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

    def notebook_tab(self):
        """Returns value of selected notebook window"""
        return self.notebook.selected_tab()

    def notebook_selection(self):
        """Returns value of current notebook selection"""
        return self.notebook.selection()

    def notebook_item(self, index):
        """Returns a specific item name from the list"""
        return self.notebook.get_item(index)

    def add_items(self, qlist):
        """Signals to notebook to add items"""
        self.notebook.add_items(qlist)

    def remove_items(self, indices):
        """Signals to notebook to remove items"""
        self.notebook.remove_items(indices)

class QueryNotebook(ttk.Notebook):
    def __init__(self, parent=None, other_widget=None):
        ttk.Notebook.__init__(self, parent)
        self.seqs = SeqScrollBox(self, other_widget)
        self.hmms = HMMScrollBox(self, other_widget)
        self.msas = MSAScrollBox(self, other_widget)
        self.add(self.seqs, text='Seq Queries')
        self.add(self.hmms, text='HMM Queries')
        self.add(self.msas, text='MSA Queries')
        self.pack(expand=YES, fill=BOTH)

    def selected_tab(self):
        """Returns the type associated with the chosen window"""
        curr_tab = self.select()
        if curr_tab == str(self.seqs):
            return 'seq'
        elif curr_tab == str(self.hmms):
            return 'hmm'
        else:
            return 'msa' # has to be one of the three

    def selection(self):
        """Returns the current selection of the widget"""
        tab = self.selected_tab()
        if tab == 'seq':
            return self.seqs.selection()
        elif tab == 'hmm':
            return self.hmms.selection()
        else:
            return self.msas.selection()

    def get_item(self, index):
        """Returns the item name corresponding to index"""
        tab = self.selected_tab()
        if tab == 'seq':
            return self.seqs.get(index)
        elif tab == 'hmm':
            return self.hmms.get(index)
        else:
            return self.msas.get(index)

    def add_items(self, qlist):
        """Adds each item to the widget"""
        seq_queries = []
        hmm_queries = []
        msa_queries = []
        for k,v in qlist:
            if v.search_type == 'seq':
                seq_queries.append([k,v])
            elif v.search_type == 'hmm':
                hmm_queries.append([k,v])
            else:
                msa_queries.append([k,v])
        self.seqs.add_items(seq_queries)
        self.hmms.add_items(hmm_queries)
        self.msas.add_items(msa_queries)

    def remove_items(self, indices):
        """Removes items from widget"""
        tab = self.selected_tab()
        if tab == 'seq':
            self.seqs.remove_items(indices)
        elif tab == 'hmm':
            self.hmms.remove_items(indices)
        else:
            self.msas.remove_items(indices)

class QueryScrollBox(gui_util.ScrollBoxFrame):
    def __init__(self, parent=None, other_widget=None, qtype=None):
        query_db = configs['query_db']
        to_display = []
        for qid in query_db.list_entries():
            qobj = query_db[qid]
            if qobj.search_type == qtype:
                to_display.append([qid,qobj])
        gui_util.ScrollBoxFrame.__init__(self, parent,
                items=to_display, # display known queries to start
                other_widget=other_widget) # info frame for display
        self.qdb = query_db

    def onSelect(self, *args):
        """
        If only one item is selected, display information corresponding to that
        query object in QueryInfo widget; if more than one item is selected, do
        nothing; implement in each subclass.
        """
        raise NotImplementedError

class SeqScrollBox(QueryScrollBox):
    def __init__(self, parent=None, other_widget=None):
        QueryScrollBox.__init__(self, parent, other_widget, 'seq')

    def onSelect(self, *args):
        """
        Checks whether only a single item is selected and then, if so, updates
        the display panel; if more than one selected does nothing.
        """
        selected = self.listbox.curselection()
        if len(selected) > 1:
            pass
        else:
            to_display = []
            item = self.get(selected)
            qobj = self.qdb[item]
            to_display.extend([
                ('Sequence Query Information' + '\n'),
                ('Query Identity: ' + str(qobj.identity)),
                ('Query Name: ' + str(qobj.name)),
                ('Query Alphabet: ' + str(qobj.alphabet)),
                ('Associated Record: ' + str(qobj.record))])
            if len(qobj.raccs) > 0:
                to_display.append('Redundant Accessions:')
                for racc in qobj.raccs: # raccs is a list of lists
                    to_display.append(str(racc[0]) + ' ' + str(racc[1]))
            self.other.update_info(to_display)

class HMMScrollBox(QueryScrollBox):
    def __init__(self, parent=None, other_widget=None):
        QueryScrollBox.__init__(self, parent, other_widget, 'hmm')

    def onSelect(self, *args):
        """
        Checks whether only a single item is selected and then, if so, updates
        the display panel; if more than one selected does nothing.
        """
        selected = self.listbox.curselection()
        if len(selected) > 1:
            pass
        else:
            to_display = []
            item = self.get(selected)
            qobj = self.qdb[item]
            to_display.extend([
                ('HMM Query Information' + '\n'),
                ('Query Identity: ' + str(qobj.identity)),
                ('Query Name: ' + str(qobj.name)),
                ('Query Alphabet: ' + str(qobj.alphabet))])
            if qobj.num_seqs != 0:
                to_display.append(
                    ('Number of Sequences: ' + str(qobj.num_seqs)))
            if len(qobj.associated_queries) > 0:
                to_display.append('Associated Queries:')
                for qid in qobj.associated_queries:
                    to_display.append(qid)
            self.other.update_info(to_display)

class MSAScrollBox(QueryScrollBox):
    def __init__(self, parent=None, other_widget=None):
        QueryScrollBox.__init__(self, parent, other_widget, 'msa')

    def onSelect(self, *args):
        pass

class QueryInfo(gui_util.InfoPanel):
    def __init__(self, parent=None):
        gui_util.InfoPanel.__init__(self, parent)

#################################
# Code for adding query objects #
#################################

class AddQueryFrame(Frame):
    def __init__(self, parent=None, query_widget=None, qtype=None, columns=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.other = query_widget
        self.qtype = qtype
        self.qdb = configs['query_db']
        self.pack(expand=YES, fill=BOTH)
        self.columns = QueryColumns(self)
        # add toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        if self.qtype == 'seq':
            self.buttons.extend([('Add by File', self.onAddFile, {'side':LEFT}),
                                ('Add Manually', self.onAddMan, {'side':LEFT})])
        else:
            self.buttons.append(('Add by File', self.onAddFile, {'side':LEFT}))
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Add all entries in 'To be Added' side of columns to parent widget"""
        to_add = self.columns.get_to_add() # returns a dict
        submission = QuerySubmission(to_add, self.other)
        submission.submit()
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

    def onAddFile(self):
        """Add queries by whole file"""
        window = Toplevel()
        if self.qtype == 'seq':
            AddSeqFileFrame(window, self.columns)
        elif self.qtype == 'hmm':
            AddHMMFileFrame(window, self.columns)
        elif self.qtype == 'msa':
            AddMSAFileFrame(window, self.columns)

    def onAddMan(self):
        """
        Add queries by manual input; currently limited only to sequence-based
        queries as both HMM- and MSA-based queries are one-per-file anyway and
        the manual interface would likely be unnecessary.
        """
        window = Toplevel()
        AddSeqManFrame(window, self.columns)

class QuerySubmission:
    """
    Sorts out adding queries to the main query widget. Namely, determines if any
    need to run searches for raccs and then runs those searches before adding all
    queries to the other widget; else just adds them
    """
    def __init__(self, qdict, other_widget):
        self.qdict = qdict
        self.other = other_widget # to add the queries to
        self.qdb = configs['query_db']
        self.mqdb = configs['misc_queries']
        self.qlist = [] # all queries

    def submit(self):
        """
        Determines whether or not to run searches, either runs them or not, and
        then signals query widget to update with new queries.
        """
        seqs_to_search = [] # those that need blast searches performed
        hmms_to_search = [] # different lists for each
        for k,v in self.qdict.items():
            # no matter what, add to query db now
            self.qdb.add_entry(k,v)
            if v.search_type == 'seq':
                if (v.racc_mode != 'no' and not v.search_ran): # need raccs
                    seqs_to_search.append(k) # works by qid
            elif v.search_type == 'hmm':
                for qid in v.associated_queries:
                    qobj = self.mqdb[qid]
                    if (qobj.racc_mode != 'no' and not qobj.search_ran):
                        hmms_to_search.append(qid)
            else: # for msa
                pass
            # no matter what, append to list for query widget
            self.qlist.append([k,v])
        if len(seqs_to_search) > 0: # searches to be run
            self.run_racc_search(seqs_to_search, 'seq')
        if len(hmms_to_search) > 0:
            self.run_racc_search(hmms_to_search, 'hmm')
        else:
            self.other.add_queries(self.qlist) # add to other widget's display

    def run_racc_search(self, qid_list, qtype):
        """Creates a search object and runs the search"""
        # create a randomly unique search name
        search_name = ''.join([random.choice(string.ascii_letters) for i in range(20)])
        self.sobj = search_obj.Search(
                name=search_name,
                algorithm='blast',
                q_type=None,
                db_type=None,
                queries=qid_list,
                databases=None)
        window = Toplevel()
        prog_frame = new_threaded_search.ProgressFrame(self.sobj, 'racc', window,
                other_widget=self, callback=self.racc_callback, callback_args=(qtype,))
        prog_frame.run()

    def racc_callback(self, qtype):
        """Parses output files, adds accs to qobjs, and then removes all db entries"""
        configs['threads'].remove_thread()
        self.udb = configs['result_db']
        try:
            for uid in self.sobj.list_results():
                robj = self.udb[uid]
                if qtype == 'seq':
                    qobj = self.qdb[robj.query]
                elif qtype == 'hmm':
                    qobj = self.mqdb[robj.query]
                self.add_self_blast(qobj, robj.parsed_result)
        except:
            pass # freak out
        finally:
            # don't want to keep these in the db
            for rid in self.sobj.results:
                self.udb.remove_entry(rid)
            # add to other widget's display
            self.other.add_queries(self.qlist)

    def add_self_blast(self, qobj, blast_result):
        """Adds hits to qobj attribute before removal"""
        #print('adding self blast')
        lines = []
        seen = set()
        for hit in blast_result.descriptions:
            #print(hit)
            new_title = search_util.remove_blast_header(hit.title)
            if not new_title in seen:
                lines.append([new_title, hit.e])
                seen.add(new_title)
        qobj.add_all_accs(lines)

class QueryColumns(ttk.Panedwindow):
    def __init__(self, parent=None, p_text='Possible Queries', a_text='To be Added'):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.pack(expand=YES, fill=BOTH)
        self.query_list = QueryListFrame(self, p_text)
        self.added_list = AddedListFrame(self, a_text)
        self.add(self.query_list)
        self.add(self.added_list)
        # to avoid AttributeError, link widgets after each is assigned
        self.query_list.link_widget(self.added_list)
        self.added_list.link_widget(self.query_list)

    def add_queries(self, query_list):
        """
        Called from adding windows, adds new queries to widget;
        Before these were added to query_list but now add to added_list, as we
        assume the user wants the queries as a default
        """
        self.added_list.lbox_frame.add_items(query_list)

    def add_possibilities(self, query_list):
        """Same as add_queries, but do put in the query_list"""
        self.query_list.lbox_frame.add_items(query_list)

    def get_to_add(self):
        """Returns the dictionary of objects to add"""
        return self.added_list.to_add()

class QueryListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', lambda x:self.onAdd())
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
        self.lbox_frame.remove_items(selected) # also removes from internal list and dict

class AddedListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', lambda x:self.onRemove())
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
        self.lbox_frame.remove_items(selected)

    def to_add(self):
        """Returns dictionary associated with items"""
        return self.lbox_frame.item_dict

class AddSeqFileFrame(Frame):
    def __init__(self, parent, other_widget):
        Frame.__init__(self, parent)
        self.parent = parent
        self.other = other_widget
        self.rdb = configs['record_db']
        self.pack(expand=YES, fill=BOTH)
        # File information
        Label(self, text='Query file information',
                anchor='w').pack(expand=YES, fill=X, side=TOP)
        self.sel_file = input_form.FileValueForm(self)
        # Query(ies) alphabet
        self.alphabet = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Query file alphabet')
        # Record for all queries, if possible
        self.record = gui_util.ComboBoxFrame(self,
                list(self.rdb.list_entries()), # function returns an iterator
                labeltext='Associated record')
        # Whether or not to add raccs
        self.add_raccs = gui_util.RadioBoxFrame(self,
                [('No','no'), ('Auto','auto'), ('Manual','manual')],
                labeltext='Add redundant accessions?')
        # Now add toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Get queries from file and add them to the columns widget"""
        queries = query_file.FastaFile(self.sel_file.content['Filename'].get(),
            self.alphabet.selected.get(), self.record.selected.get(),
            self.add_raccs.selected.get()).get_queries()
        self.other.add_queries(queries)
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

class AddHMMFileFrame(Frame):
    def __init__(self, parent, other_widget):
        Frame.__init__(self, parent)
        self.parent = parent
        self.other = other_widget
        self.pack(expand=YES, fill=BOTH)
        # Main file information
        Label(self, text='HMM file information',
                anchor='w').pack(expand=YES, fill=X, side=TOP)
        self.sel_file = input_form.FileValueForm(self)
        # Other file information
        Label(self, text='MSA file information',
                anchor='w').pack(expand=YES, fill=X, side=TOP)
        self.msa_file = input_form.FileValueForm(self)
        Label(self, text='Sequences file information',
                anchor='w').pack(expand=YES, fill=X, side=TOP)
        self.seq_file = input_form.FileValueForm(self)
        # Query(ies) alphabet
        self.alphabet = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Query file alphabet')
        # Associated queries, if wanted
        self.queries = []
        self.qbox = gui_util.ComboBoxFrame(self,
                self.queries, labeltext='Associated queries')
        # Now add toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT}),
                        ('Add Associated Query(ies)', self.onAddQ, {'side':LEFT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Get queries from file and add them to the columns widget"""
        queries = []
        name,hmm_obj = query_file.HMMFile(self.sel_file.content['Filename'].get(),
            self.alphabet.selected.get()).get_query()
        hmm_obj.msa_file = self.msa_file.content['Filename'].get()
        hmm_obj.add_msa()
        hmm_obj.seq_file = self.seq_file.content['Filename'].get()
        hmm_obj.add_seqs()
        if len(self.queries) > 0:
            for qid in self.queries:
                hmm_obj.add_query(qid)
        queries.append([name,hmm_obj])
        self.other.add_queries(queries) # expects a list
        self.parent.destroy()

    def onCancel(self):
        self.parent.destroy()

    def onAddQ(self):
        """Pops up a query window similar to the query list view"""
        window = Toplevel()
        AddSeqQueryFrame(window, self, 'seq')

    def add_items(self, query_list):
        """Adds items to internal list"""
        if len(self.queries) == 0:
            self.queries = query_list
        else:
            for key in query_list:
                self.queries.append(key)
        self.qbox.add_items(query_list)

class AddSeqQueryFrame(AddQueryFrame):
    """
    Like Add Query Frame, but specifically offers choice of already present
    sequence-based queries to user. Any additional queries that are added are
    also added to the main query_db.
    """
    def __init__(self, parent, other_widget, qtype):
        AddQueryFrame.__init__(self, parent, other_widget, qtype)
        self.qdb = configs['query_db']
        queries = []
        for qid in self.qdb.list_entries():
            qobj = self.qdb[qid]
            if qobj.search_type == 'seq':
                queries.append((qid,qobj))
        self.columns.add_possibilities(queries)

    def onSubmit(self):
        """Adds the selected queries to the HMM object"""
        mqdb = configs['misc_queries'] # hidden node from user
        to_add = self.columns.get_to_add() # returns a dict
        qlist = []
        for k,v in to_add.items():
            mqdb.add_entry(k,v)
            qlist.append(k)
        self.other.add_items(qlist) # add to other widget's display
        self.parent.destroy()

class AddMSAFileFrame(Frame):
    pass

class AddSeqManFrame(Frame):
    def __init__(self, parent=None, other_widget=None):
        Frame.__init__(self, parent)
        self.other = other_widget
        self.pack(expand=YES, fill=BOTH)
        self.layout = AddManualGui(self)
        # toolbar and buttons
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
            self.other.query_list.lbox_frame.add_items(qid)
            self.other.query_list.queries[qid] = qobj
        except(AttributeError):
            # do not allow raccs if no record specified
            messagebox.showwarning('Incompatible options',
                'Cannot choose to add redundant accessions without associated record')

    def onCancel(self):
        """Closes the window without actually adding queries"""
        self.parent.destroy()

class AddManualGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.pack(expand=YES, fill=BOTH)
        self.seq_entry = SeqEntryFrame(self)
        self.seq_info = SeqInfoFrame(self)
        self.add(self.seq_entry)
        self.add(self.seq_info)

class SeqEntryFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Input Sequence').pack(expand=YES, fill=X, side=TOP)
        # will eventually need to implement a much more complex interface
        # for the canvas, and add scrollbars, etc.
        self.entry = Canvas(width=200, height=400, bg='white')

class SeqInfoFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.rdb = configs['record_db']
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Sequence Information').pack(expand=YES, fill=X, side=TOP)
        self.names = input_form.DefaultValueForm(
                [('Identity',''),('Name',''),('Description','')],
                self)
        self.qtype = gui_util.RadioBoxFrame(self,
                [('Seq','seq'), ('HMM','hmm')],
                labeltext='Query type')
        self.alphabet = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self,
                self.rdb.list_entries(), # record db keys
                labeltext='Associated record')
        self.add_raccs = gui_util.RadioBoxFrame(self,
                [('No','no'), ('Auto','auto'),('Manual','man')],
                labeltext='Add Redundant Accessions?')

#############################################
# Code for modifying existing query objects #
#############################################

class ModifySeqQuery(Frame):
    def __init__(self, parent=None, qobj=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.qobj = qobj
        self.qdb = configs['query_db']
        self.pack(expand=YES, fill=BOTH)
        self.layout = ModSeqWindow(self, qobj)
        # tool bar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        new_attrs = {}
        info = self.layout.query_info
        for row in info.names.row_list: # can we get without for-loop?
            if row.label_text == 'Identity':
                new_attrs['identity'] = row.entry.get()
            elif row.label_text == 'Name':
                new_attrs['name'] = row.entry.get()
            else:
                new_attrs['description'] = row.entry.get()
        new_attrs['alphabet'] = info.alphabet.selected.get()
        new_attrs['record'] = info.record.selected.get()
        for attr,value in new_attrs.items():
            setattr(self.qobj,attr,value) # change values, or reset unchanged ones
        racc_window = self.layout.added_list.lbox_frame
        raccs = []
        for item in racc_window.item_list:
            title,evalue = racc_window.item_dict[item] # value is title,evalue tuple
            raccs.append([title,evalue])
        self.qobj.add_raccs(raccs)
        self.parent.destroy()

    def onCancel(self):
        """Closes the window without actually modifying raccs"""
        self.parent.destroy()

class ModSeqWindow(ttk.Panedwindow):
    def __init__(self, parent=None, qobj=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.qobj = qobj
        self.pack(expand=YES, fill=BOTH)
        self.query_info = SeqQueryInfo(self)
        self.blast_list = BlastListFrame(self, 'BLAST Hits')
        self.added_list = BlastAddedFrame(self, 'To be Added')
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
        for row in self.query_info.names.row_list:
            if row.label_text == 'Identity':
                row.entry.insert(0,self.qobj.identity)
            elif row.label_text == 'Name':
                row.entry.insert(0,self.qobj.name) # insert name
            else:
                row.entry.insert(0,self.qobj.description)
        self.query_info.alphabet.selected.set(self.qobj.alphabet) # select db type
        self.query_info.record.selected.set(self.qobj.record) # select record
        # Now populate both racc windows
        all_accs = []
        raccs = []
        for index,item in enumerate(self.qobj.all_accs): # item is a tuple
            display_string = str(item[0]) + '  ' + str(item[1])
            if item in self.qobj.raccs:
                raccs.append([display_string,item,index])
            else:
                all_accs.append([display_string,item])
        self.blast_list.lbox_frame.add_items(all_accs)
        self.added_list.lbox_frame.add_items(raccs, mode='index')

class SeqQueryInfo(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.rdb = configs['record_db']
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Query Information').pack(expand=YES, fill=X, side=TOP)
        self.names = input_form.DefaultValueForm(
                [('Identity',''), ('Name',''), ('Description','')],
                self)
        self.alphabet = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.record = gui_util.ComboBoxFrame(self,
                list(self.rdb.list_entries()), # record db keys
                labeltext='Associated record')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

class BlastListFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', lambda x:self.onAdd())

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
        self.lbox_frame.remove_items(selected)

class BlastAddedFrame(Frame):
    def __init__(self, parent, text):
        Frame.__init__(self, parent)
        self.lbox_frame = gui_util.ScrollBoxFrame(self, text)
        self.lbox_frame.listbox.bind('<Return>', lambda x:self.onRemove())

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
        self.lbox_frame.remove_items(selected)

class ModifyHMMQuery(Frame):
    def __init__(self, parent=None, qobj=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.qobj = qobj
        self.qdb = configs['query_db']
        self.mqdb = configs['misc_queries']
        self.pack(expand=YES, fill=BOTH)
        self.layout = ModHMMWindow(self, qobj)
        # tool bar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Submits and signals back to the other widget to do something"""
        new_attrs = {}
        info = self.layout.query_info
        for row in info.names.row_list: # can we get without for-loop?
            if row.label_text == 'Identity':
                new_attrs['identity'] = row.entry.get()
            elif row.label_text == 'Name':
                new_attrs['name'] = row.entry.get()
            else:
                new_attrs['description'] = row.entry.get()
        new_attrs['alphabet'] = info.alphabet.selected.get()
        for attr,value in new_attrs.items():
            setattr(self.qobj,attr,value) # change values, or reset unchanged ones
        # Check for current raccs in window and add to dict first
        self.layout.add_current_raccs()
        # Add raccs to query objects now from dict
        for qid in self.layout.racc_dict.keys():
            qobj = self.mqdb[qid]
            qobj.add_raccs(self.layout.racc_dict[qid]['raccs']) # should be a list of raccs
        self.parent.destroy()

    def onCancel(self):
        """Closes the window without actually modifying raccs"""
        self.parent.destroy()

class ModHMMWindow(ttk.Panedwindow):
    def __init__(self, parent=None, qobj=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.qobj = qobj
        self.mqdb = configs['misc_queries']
        self.pack(expand=YES, fill=BOTH)
        self.query_info = HMMQueryInfo(self, self.qobj)
        self.blast_list = BlastListFrame(self, 'BLAST Hits')
        self.added_list = BlastAddedFrame(self, 'To be Added')
        self.add(self.query_info)
        self.add(self.blast_list)
        self.add(self.added_list)
        # to avoid AttributeError, link widgets after each is assigned
        self.blast_list.link_widget(self.added_list)
        self.added_list.link_widget(self.blast_list)
        # set windows to current state of selected query
        self.populate_windows()
        # keep a dict of all associated query raccs
        self.racc_dict = {}
        self.populate_racc_dict()
        # set an instance value to current qid
        self.curr_qid = None

    def populate_windows(self):
        """
        Retrieves information from the passed in query and changes the child
        display windows to display this information
        """
        for row in self.query_info.names.row_list:
            if row.label_text == 'Identity':
                row.entry.insert(0,self.qobj.identity)
            elif row.label_text == 'Name':
                row.entry.insert(0,self.qobj.name) # insert name
            else:
                row.entry.insert(0,self.qobj.description)
        self.query_info.alphabet.selected.set(self.qobj.alphabet) # select db type

    def populate_racc_dict(self):
        """
        For each query in the associated queries list of the hmm object, adds an
        entry with the current value of both all accs and raccs for use with the
        populate_acc_windows function; if submitted, this dict is also used to
        update the relevant query object in the misc_queries DB.
        """
        for qid in self.qobj.associated_queries:
            self.racc_dict[qid] = {} # nested dictionary easiest for use
            qobj = self.mqdb[qid]
            self.racc_dict[qid]['all_accs'] = qobj.all_accs
            self.racc_dict[qid]['raccs'] = qobj.raccs

    def populate_acc_windows(self, qid):
        """
        Called when the value of the associated queries combobox changes, grabs
        the relevant query object from the misc_queries db and populates the
        windows with it.
        """
        # first attempt to set
        if self.curr_qid:
            self.add_raccs_to_dict()
        # clear windows
        self.blast_list.lbox_frame.clear()
        self.added_list.lbox_frame.clear()
        # attempt to re-populate the windows
        try:
            #qobj = self.mqdb[qid]
            qdict = self.racc_dict[qid]
            # Now populate both racc windows
            all_accs = []
            raccs = []
            for index,item in enumerate(qdict['all_accs']): # item is a tuple
                display_string = str(item[0]) + '  ' + str(item[1])
                if item in qdict['raccs']:
                    raccs.append([display_string,item,index])
                else:
                    all_accs.append([display_string,item])
            self.blast_list.lbox_frame.add_items(all_accs)
            self.added_list.lbox_frame.add_items(raccs, mode='index')
        except KeyError: # qid not in dict, possibly empty string
            pass
        finally:
            self.curr_qid = qid # no matter what change the current qid

    def add_raccs_to_dict(self, qid=None):
        """
        Called before changing the listbox entries, adds the current value of the
        racc listbox to the relevant qid entry in self.racc_dict.
        """
        if not qid:
            qid = self.curr_qid
        raccs = []
        racc_window = self.added_list.lbox_frame
        for item in racc_window.item_list:
            title,evalue = racc_window.item_dict[item] # value is title,evalue tuple
            raccs.append([title,evalue])
        self.racc_dict[qid]['raccs'] = raccs

    def add_current_raccs(self):
        """
        Called on parent submit; ensures that raccs chosen in current window are
        also added to dict (otherwise not added because no switch occurred)
        """
        curr_qid = self.query_info.curr_query()
        self.add_raccs_to_dict(curr_qid)

class HMMQueryInfo(Frame):
    def __init__(self, parent=None, hmm_obj=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.hobj = hmm_obj
        self.pack(expand=YES, fill=BOTH)
        Label(self, text='Query Information').pack(expand=YES, fill=X, side=TOP)
        self.names = input_form.DefaultValueForm(
                [('Identity',''), ('Name',''), ('Description','')],
                self)
        self.alphabet = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Sequence alphabet')
        self.assoc_queries = gui_util.ComboBoxFrame(self,
                list(self.hobj.associated_queries),
                labeltext='Associated queries',
                select_function=self.onSelect)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

    def curr_query(self):
        """Gets current value of associated queries combobox"""
        return self.assoc_queries.get()

    def onSelect(self):
        """Signals back to parent widget to populate listboxes"""
        qid = self.curr_query()
        self.parent.populate_acc_windows(qid)

class ModifyMSAQuery(Frame):
    def __init__(self, parent=None, qobj=None):
        pass
