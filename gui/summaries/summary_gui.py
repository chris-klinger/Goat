"""
This module contains code for a user interface to summarizing results in Goat.
User is asked to choose between one or two searches to summarize, and then
depending on this choice to fill in different forms for relevant information.
"""

import os
from tkinter import *
from tkinter import ttk, messagebox, filedialog

from bin.initialize_goat import configs

from gui.util import gui_util, input_form
from summaries import summary_obj, summarizer, summary_writer
from util import util
from util.sequences import seqs_from_summary
# For summary selection code
from gui.queries import main_query_gui

################################
# Code for summarizing results #
################################

class SearchSummaryFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.mdb = configs['summary_db']
        self.qdb = configs['query_db']
        self.sdb = configs['search_db']
        self.udb = configs['result_db']
        self._dbs = (self.mdb, self.qdb, self.sdb, self.udb)
        self.pack(expand=YES, fill=BOTH)
        self.radio_box = gui_util.RadioBoxFrame(self,
            choices=(['One','one'],['Two','two']),
            labeltext='Summarize how many searches?')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close dbs"""
        self.parent.destroy()

    def onCancel(self):
        self.onClose()

    def onSubmit(self):
        """Close window and call another window for user input"""
        window = Toplevel()
        if self.radio_box.selected == 'one':
            OneSearchFrame(self.mdb, self.qdb, self.sdb, self.udb, window)
        else:
            TwoSearchFrame(self.mdb, self.qdb, self.sdb, self.udb, window)
        self.parent.destroy()

class OneSearchFrame(Frame):
    def __init__(self, summary_db, query_db, search_db, result_db, parent):
        Frame.__init__(self, parent)
        self.mdb = summary_db
        self.qdb = query_db
        self.sdb = search_db
        self.udb = result_db
        self._dbs = (self.mdb, self.qdb, self.sdb, self.udb)
        self.pack(expand=YES, fill=BOTH)
        self.fwd_search = gui_util.ComboBoxFrame(self,
                choices=list(self.sdb.list_entries()), # generator
                labeltext='Search to summarize')
        self.params = input_form.DefaultValueForm((['Summary name',''],
            ['Minimum evalue',''],['Next hit evalue',''],['Max hits','']), self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close dbs and destroy window"""
        for db in self._dbs:
            db.close()
        self.parent.destroy()

    def onCancel(self):
        """Quit without summarizing; close dbs"""
        self.onClose()

    def onSubmit(self):
        """Summarize and add summary to db, close after"""
        fwd_search = self.fwd_search.selected
        fwd_sobj = self.sdb[fwd_search]
        for row in self.params.row_list:
            value = row.entry.get()
            if row.label_text == 'Summary name':
                name = value # should add a clause so that it can't be ''
            if row.label_text == 'Minimum evalue':
                fwd_evalue = (float(value) if not value == '' else None)
            elif row.label_text == 'Next hit evalue':
                next_evalue = (float(value) if not value == '' else None)
            elif row.label_text == 'Max hits':
                fwd_max_hits = (int(value) if not value == '' else None)
        sum_obj = summary_obj.Summary(fwd_search, fwd_sobj.q_type,
                fwd_sobj.db_type, fwd_sobj.algorithm, fwd_evalue,
                fwd_max_hits, next_hit_evalue_cutoff=next_evalue)
        summer = summarizer.SearchSummarizer(sum_obj,
                self.qdb, self.sdb, self.udb)
        summer.summarize_one_result()
        self.mdb.add_entry(name, sum_obj)
        self.mdb.commit()
        self.onClose()

class TwoSearchFrame(Frame):
    def __init__(self, summary_db, query_db, search_db, result_db, parent):
        Frame.__init__(self, parent)
        self.mdb = summary_db
        self.qdb = query_db
        self.sdb = search_db
        self.udb = result_db
        self._dbs = (self.qdb, self.sdb, self.udb)
        self.pack(expand=YES, fill=BOTH)
        self.fwd_search = gui_util.ComboBoxFrame(self,
                choices=list(self.sdb.list_entries()), # generator
                labeltext='Forward search to summarize')
        self.rev_search = gui_util.ComboBoxFrame(self,
                choices=list(self.sdb.list_entries()), # generator
                labeltext='Reverse search to summarize')
        self.params = input_form.DefaultValueForm((['Summary name','SummTest'],
            ['Minimum forward evalue',0.05],['Minimum reverse evalue',0.05],
            ['Next hit evalue',2],['Max forward hits',10],
            ['Max reverse hits',10]), self)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close dbs and destroy window"""
        for db in self._dbs:
            db.commit()
        self.parent.destroy()

    def onCancel(self):
        """Quit without summarizing; close dbs"""
        self.onClose()

    def onSubmit(self):
        """Summarize and add summary to db, close after"""
        fwd_search = self.fwd_search.selected.get()
        #print(fwd_search)
        fwd_sobj = self.sdb[fwd_search]
        rev_search = self.rev_search.selected.get()
        #print(rev_search)
        rev_sobj = self.sdb[rev_search]
        for row in self.params.row_list:
            value = row.entry.get()
            if row.label_text == 'Summary name':
                name = value # should add a clause so that it can't be ''
            if row.label_text == 'Minimum forward evalue':
                fwd_evalue = (float(value) if not value == '' else None)
            if row.label_text == 'Minimum reverse evalue':
                rev_evalue = (float(value) if not value == '' else None)
            elif row.label_text == 'Next hit evalue':
                next_evalue = (float(value) if not value == '' else None)
            elif row.label_text == 'Max forward hits':
                fwd_max_hits = (int(value) if not value == '' else None)
            elif row.label_text == 'Max reverse hits':
                rev_max_hits = (int(value) if not value == '' else None)
        sum_obj = summary_obj.Summary(fwd_search, fwd_sobj.q_type,
                fwd_sobj.db_type, fwd_sobj.algorithm, fwd_evalue,
                fwd_max_hits, rev_search, rev_sobj.q_type, rev_sobj.db_type,
                rev_sobj.algorithm, rev_evalue, rev_max_hits, next_evalue)
        summer = summarizer.SearchSummarizer(sum_obj)
        summer.summarize_two_results()
        #print()
        #print()
        #print('\n' + str(sum_obj))
        #for qid in sum_obj.queries:
            #print('\t' + qid)
            #qobj = sum_obj.fetch_query_summary(qid)
            #for uid in qobj.db_list:
                #print('\t\t' + uid)
                #uobj = qobj.fetch_db_summary(uid)
                #for hit in uobj.positive_hit_list:
                    #hobj = uobj.hits[hit]
                    #for k,v in hobj.__dict__.items():
                        #print(str(k) + ' ' + str(v))
                    #print('\t\t\t' + str(hit))
        self.mdb.add_entry(name, sum_obj)
        self.mdb.commit()
        self.onClose()

###########################################
# Code for summarizing multiple summaries #
###########################################

class SummSummaryFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.mdb = configs['summary_db']
        self.pack(expand=YES, fill=BOTH)
        self.summ_list = []
        self.name = input_form.DefaultValueForm(
                [('Summary name','')], self)
        self.columns = SummaryColumns(self)
        # Toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """
        Collects the list of all summaries in the 'To be Summed' window, and then
        creates a new summarizer object to hold them.
        """
        summ_list = self.columns.get_to_add()
        #print(summ_list)
        summ_name = self.name.get('Summary name')
        summ_obj = summary_obj.Summary(
                fwd_search=None, # otherwise required values are None here
                fwd_qtype=None,
                fwd_dbtype=None,
                fwd_algorithm=None,
                mode='summary') # make sure to specify type of summary
        #print(summ_obj)
        summer = summarizer.SummSummarizer(summ_obj, summ_list)
        summer.add_summaries()
        #print('adding summary obj to database')
        self.mdb.add_entry(summ_name, summ_obj)
        self.mdb.commit()
        #print('running cancel function')
        self.onCancel()

class SummaryColumns(ttk.Panedwindow):
    def __init__(self, parent, p_text='Possible Summaries', a_text='To be Summed'):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.mdb = configs['summary_db']
        self.pack(expand=YES, fill=BOTH)
        self.summaries = main_query_gui.BlastListFrame(self, p_text)
        self.added = main_query_gui.BlastAddedFrame(self, a_text)
        self.add(self.summaries)
        self.add(self.added)
        # Link widgets
        self.summaries.link_widget(self.added)
        self.added.link_widget(self.summaries)
        # Now add information
        self.add_possibilities()

    def add_possibilities(self):
        """Override superclass to add all summary_db entries instead"""
        to_add = []
        for index,mid in enumerate(self.mdb.list_entries()):
            self.summaries.lbox_frame.item_index[mid] = index # keep track of index
            self.added.lbox_frame.item_index[mid] = index
            to_add.append([mid,'']) # need a tuple
        self.summaries.lbox_frame.add_items(to_add)

    def get_to_add(self):
        """Returns a list of the summaries in the added frame"""
        return self.added.lbox_frame.item_list

##############################
# Code for viewing summaries #
##############################

class SummaryViewer(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.mdb = configs['summary_db']
        self.udb = configs['result_db']
        self.parent = parent
        self.summaries = SummaryGui(self.mdb, self.udb, self)
        self.pack(expand=YES, fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Remove', self.onRemove, {'side':LEFT}),
                        ('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onClose(self):
        """Close associated database and destroy window"""
        self.parent.destroy()

    def onRemove(self):
        """Removes a summary object and all associated sub-objects. Removal should
        be by whole summary, not individual sub-objects, and in fact, perhaps may
        make this an illegal operation?"""
        #item_name = self.summaries.summary_tree.focus()
        #item = self.summaries.summary_tree.item(item_name)
        #if item['tags'][0] == 'summary':
        #    self.mdb.remove_entry(item['text'])
        #else: # do we want to allow removal of anything other than summaries?
        #    pass
        #self.summaries.summary_tree.update() # lastly, call for an update
        item = self.summaries.notebook_item()
        mtype = self.summaries.notebook_tab()
        if item['tags'][0] == 'summary':
            mid = item['text']
            if messagebox.askyesno(
                    message = "Delete summary {}?".format(mid),
                    icon='question', title='Remove summary'):
                self.mdb.remove_entry(mid)
                self.summaries.redraw_tree(mtype)

    def onSubmit(self):
        """Commits any changes and destroys window"""
        self.mdb.commit()
        self.udb.commit()
        self.onClose()

    def onCancel(self):
        """Same as onClose"""
        self.onClose()

class SummaryGui(ttk.PanedWindow):
    def __init__(self, summary_db, result_db, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.info_frame = ResultInfo(self)
        #self.summary_tree = SummaryTree(summary_db, result_db, self.info_frame, self)
        self.notebook = SummaryNotebook(self, self.info_frame)
        self.add(self.notebook)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

    def notebook_tab(self):
        return self.notebook.selected_tab()

    def notebook_item(self):
        return self.notebook.get_item()

    def redraw_tree(self, mtype):
        self.notebook.redraw_tree(mtype)

class SummaryNotebook(ttk.Notebook):
    def __init__(self, parent, other_widget=None):
        ttk.Notebook.__init__(self, parent)
        self.search_summs = SearchSummaryTree(self, other_widget)
        self.summary_summs = SummSummaryTree(self, other_widget)
        self.add(self.search_summs, text='From Searches')
        self.add(self.summary_summs, text='From Summaries')

    def selected_tab(self):
        """Returns the type associated with the chosen window"""
        curr_tab = self.select()
        if curr_tab == str(self.search_summs):
            return 'search'
        else:
            return 'summary'

    def get_item(self):
        """Returns the item name corresponding to index"""
        tab = self.selected_tab()
        if tab == 'search':
            return self.search_summs.item(self.search_summs.focus())
        else:
            return self.summary_summs.item(self.summary_summs.focus())

    def redraw_tree(self, mtype):
        """Force update() on relevant child widget"""
        if mtype == 'search':
            self.search_summs.update()
        else:
            self.summary_summs.update()

class SearchSummaryTree(ttk.Treeview):
    def __init__(self, parent, other_widget=None):
        ttk.Treeview.__init__(self, parent)
        self.mdb = configs['summary_db']
        self.udb = configs['result_db']
        self.other = other_widget
        self.config(selectmode = 'browse') # one item at a time
        self.tag_bind('summary', '<Double-1>', # single click does not register properly
                callback=lambda x:self.itemClicked('summary'))
        self.tag_bind('querysum', '<Double-1>',
                callback=lambda x:self.itemClicked('querysum'))
        self.tag_bind('dbsum', '<Double-1>',
                callback=lambda x:self.itemClicked('dbsum'))
        self.tag_bind('hitlist', '<Double-1>',
                callback=lambda x:self.itemClicked('hitlist'))
        self.tag_bind('hit', '<Double-1>',
                callback=lambda x:self.itemClicked('hit'))
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def update(self):
        """Update view after removal"""
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self):
        """Builds a treeview display of searches/results"""
        counter = util.IDCounter()
        for summary in self.mdb.list_entries():
            mobj = self.mdb[summary]
            if mobj.mode == 'result':
                uniq_s = str(counter.get_new_id())
                self.insert('','end',uniq_s,text=summary,tags=('summary'))
                for qid in mobj.query_list:
                    uniq_q = str(counter.get_new_id())
                    #print(uniq_q)
                    qobj = mobj.queries[qid]
                    self.insert(uniq_s,'end',uniq_q,text=qid,tags=('querysum'))
                    for db in qobj.db_list:
                        uniq_d = str(counter.get_new_id())
                        dbobj = qobj.dbs[db]
                        self.insert(uniq_q,'end',uniq_d,text=db,tags=('dbsum'))
                        for hitlist in dbobj.lists:
                            lobj = getattr(dbobj,hitlist)
                            if not len(lobj) == 0: # don't care about empty lists
                                uniq_l = str(counter.get_new_id())
                                self.insert(uniq_d,'end',uniq_l,text=hitlist,tags=('hitlist'))
                                for hit in lobj: # object here is a simple list
                                    uniq_h = str(counter.get_new_id())
                                    #hobj = dbobj.hits[hit]
                                    self.insert(uniq_l,'end',uniq_h,text=hit,tags=('hit'))

    def itemClicked(self, tag):
        """Builds a list of information for display by ResultInfo panel for
        either searches or results; delegates formatting/display to panel"""
        item_id = self.focus() # here item should be the object itself?
        item = self.item(item_id)
        parent_list = self.get_ancestors(item_id,[])
        db_obj = self.get_item_from_db(parent_list, self.mdb)
        to_display = []
        if tag == 'summary':
            # Add forward information
            to_display.extend([
                    ('Summary Information: \n'),
                    ('Summary Name: ' + item['text']),
                    ('Number Queries: ' + str(len(db_obj.query_list))),
                    ('Forward Search: ' + db_obj.fwd),
                    ('Forward Query Type: ' + db_obj.fwd_qtype),
                    ('Forward Database Type: ' + db_obj.fwd_dbtype),
                    ('Forward Search Algorithm: ' + db_obj.fwd_algorithm),
                    ('Forward E-value Cutoff: ' + str(db_obj.fwd_evalue)),
                    ('Forward Hit Number Cutoff: ' + str(db_obj.fwd_max_hits))])
            # Add reverse information, if present
            if db_obj.rev: # not None, there is reverse stuff
                to_display.extend([
                    ('Reverse Search: ' + db_obj.rev),
                    ('Reverse Query Type: ' + db_obj.rev_qtype),
                    ('Reverse Database Type: ' + db_obj.rev_dbtype),
                    ('Reverse Search Algorithm: ' + db_obj.rev_algorithm),
                    ('Reverse E-value Cutoff: ' + str(db_obj.rev_evalue)),
                    ('Reverse Hit Number Cutoff: ' + str(db_obj.rev_max_hits))])
            # Add evalue and max cutoff information
            to_display.append('Next Hit Evalue Cutoff: ' + str(db_obj.next_evalue))
        elif tag == 'querysum':
            to_display.extend([
                    ('Query Information: \n'),
                    ('Query Name: ' + item['text']),
                    ('Number of Databases Searched In: ' + str(len(db_obj.db_list)))])
        elif tag == 'dbsum':
            to_display.extend([
                ('Database Information: \n'),
                ('Datbase Name: ' + item['text']),
                ('Status of Searches in Database: ' + db_obj.status)])
        elif tag == 'hitlist':
            name = item['text']
            if name == 'positive_hit_list':
                status = 'positive'
            elif name == 'tentative_hit_list':
                status = 'tentative'
            else: # unlikely
                status = 'unlikely'
            to_display.extend([
                ('Hit Group Information: \n'),
                ('Hit status(es): ' + status),
                ('Number of Hits: ' + str(len(db_obj)))])
        elif tag == 'hit':
            to_display.extend([
                ('Hit Information: \n'),
                ('Forward Query ID: ' + str(db_obj.fwd_id)),
                ('Forward E-value: ' + str(db_obj.fwd_evalue))])
            if db_obj.pos_rev_id: # not None
                to_display.extend([
                    ('First Positive Revese Hit ID: ' + str(db_obj.pos_rev_id)),
                    ('First Positive Reverse Hit E-value: ' + str(db_obj.pos_rev_evalue)),
                    ('First Negative Reverse Hit ID: ' + str(db_obj.neg_rev_id)),
                    ('First Negative Reverse Hit E-value: ' + str(db_obj.neg_rev_evalue)),
                    ('Reverse Hits E-value Difference: ' + str(db_obj.rev_evalue_diff))])
            to_display.append('Hit Status: ' + db_obj.status)
        self.other.update_info(to_display)

    def get_ancestors(self, item_name, item_list=[]):
        """Recurs until root node to return a list of ancestors"""
        parent = self.parent(item_name)
        item = self.item(item_name)
        item_id = item['text']
        if item_name == '': # hit root node
            return item_list[::-1]
        else:
            item_list.append(item_id)
            return self.get_ancestors(parent, item_list) # recur

    def get_item_from_db(self, item_list, obj, index=0, db_obj=None):
        """Uses the length of item_list to choose appropriate object from nested
        database objects"""
        item = item_list[0]
        if index == 0:
            new_obj = self.mdb[item]
        elif index == 1:
            new_obj = obj.queries[item]
        elif index == 2:
            new_obj = obj.dbs[item]
            db_obj = new_obj
            #print(db_obj)
        elif index == 3:
            new_obj = getattr(obj,item) # lists
        else:
            #print('DB object is: ' + str(db_obj))
            #print(item)
            new_obj = db_obj.hits[item] # go back to ResultSummary for actual hit
            #print(new_obj.fwd_id)
        if len(item_list) == 1: # only one item remaining
            return new_obj
        else:
            item_list.remove(item)
            index += 1
            return self.get_item_from_db(item_list, new_obj, index, db_obj) # recur

class SummSummaryTree(ttk.Treeview):
    def __init__(self, parent, other_widget=None):
        ttk.Treeview.__init__(self, parent)
        self.mdb = configs['summary_db']
        self.udb = configs['result_db']
        self.other = other_widget
        self.config(selectmode = 'browse') # one item at a time
        self.tag_bind('summary', '<Double-1>', # single click does not register properly
                callback=lambda x:self.itemClicked('summary'))
        self.tag_bind('querysum', '<Double-1>',
                callback=lambda x:self.itemClicked('querysum'))
        self.tag_bind('dbsum', '<Double-1>',
                callback=lambda x:self.itemClicked('dbsum'))
        self.tag_bind('hitlist', '<Double-1>',
                callback=lambda x:self.itemClicked('hitlist'))
        self.tag_bind('hit', '<Double-1>',
                callback=lambda x:self.itemClicked('hit'))
        self.make_tree()
        self.pack(expand=YES, fill=BOTH)

    def update(self):
        """Update view after removal"""
        for item in self.get_children():
            self.delete(item)
        self.make_tree()

    def make_tree(self):
        """Builds a treeview display of searches/results"""
        pass
        counter = util.IDCounter()
        for summary in self.mdb.list_entries():
            mobj = self.mdb[summary]
            if mobj.mode == 'summary':
                uniq_s = str(counter.get_new_id())
                self.insert('','end',uniq_s,text=summary,tags=('summary'))
                for qid in mobj.query_list:
                    uniq_q = str(counter.get_new_id())
                    #print(uniq_q)
                    qobj = mobj.queries[qid]
                    self.insert(uniq_s,'end',uniq_q,text=qid,tags=('querysum'))
                    for db in qobj.db_list:
                        uniq_d = str(counter.get_new_id())
                        dbobj = qobj.dbs[db]
                        self.insert(uniq_q,'end',uniq_d,text=db,tags=('dbsum'))
                        for hit in dbobj.hit_list:
                            uniq_l = str(counter.get_new_id())
                            self.insert(uniq_d,'end',uniq_l,text=hit,tags=('hit'))

    def itemClicked(self, tag):
        """Builds a list of information for display by ResultInfo panel for
        either searches or results; delegates formatting/display to panel"""
        item_id = self.focus() # here item should be the object itself?
        item = self.item(item_id)
        parent_list = self.get_ancestors(item_id,[])
        db_obj = self.get_item_from_db(parent_list, self.mdb)
        to_display = []
        if tag == 'summary':
            # Add forward information
            to_display.extend([
                    ('Summary Information: \n'),
                    ('Summary Name: ' + item['text']),
                    ('Number Queries: ' + str(len(db_obj.query_list)))])
            # Add reverse information, if present
            if db_obj.rev: # not None, there is reverse stuff
                to_display.extend([
                    ('Reverse Search: ' + db_obj.rev),
                    ('Reverse Query Type: ' + db_obj.rev_qtype),
                    ('Reverse Database Type: ' + db_obj.rev_dbtype),
                    ('Reverse Search Algorithm: ' + db_obj.rev_algorithm),
                    ('Reverse E-value Cutoff: ' + str(db_obj.rev_evalue)),
                    ('Reverse Hit Number Cutoff: ' + str(db_obj.rev_max_hits))])
            # Add evalue and max cutoff information
            to_display.append('Next Hit Evalue Cutoff: ' + str(db_obj.next_evalue))
        elif tag == 'querysum':
            to_display.extend([
                    ('Query Information: \n'),
                    ('Query Name: ' + item['text']),
                    ('Number of Databases Searched In: ' + str(len(db_obj.db_list)))])
        elif tag == 'dbsum':
            to_display.extend([
                ('Database Information: \n'),
                ('Datbase Name: ' + item['text']),
                ('Status of Searches in Database: ' + db_obj.status)])
        elif tag == 'hit':
            to_display.extend([
                ('Hit Information: \n'),
                ('Hit Status: ' + db_obj.status)])
            for hlist in db_obj.lists:
                lobj = getattr(db_obj, hlist)
                if len(lobj) > 0:
                    if hlist == 'positive_hit_list':
                        to_display.append('Summaries yielding positive result:')
                    elif hlist == 'tentative_hit_list':
                        to_display.append('Summaries yielding tentative result:')
                    else:
                        to_display.append('Summaries yielding unlikely result:')
                    to_display.append(','.join([str(mid) for mid in lobj]))
        self.other.update_info(to_display)

    def get_ancestors(self, item_name, item_list=[]):
        """Recurs until root node to return a list of ancestors"""
        parent = self.parent(item_name)
        item = self.item(item_name)
        item_id = item['text']
        if item_name == '': # hit root node
            return item_list[::-1]
        else:
            item_list.append(item_id)
            return self.get_ancestors(parent, item_list) # recur

    def get_item_from_db(self, item_list, obj, index=0, db_obj=None):
        """Uses the length of item_list to choose appropriate object from nested
        database objects"""
        item = item_list[0]
        if index == 0:
            new_obj = self.mdb[item]
        elif index == 1:
            new_obj = obj.queries[item]
        elif index == 2:
            new_obj = obj.dbs[item]
        else:
            new_obj = obj.hits[item]
        if len(item_list) == 1: # only one item remaining
            return new_obj
        else:
            item_list.remove(item)
            index += 1
            return self.get_item_from_db(item_list, new_obj, index, db_obj) # recur

class ResultInfo(gui_util.InfoPanel):
    def __init__(self, parent=None):
        gui_util.InfoPanel.__init__(self, parent)

###################################################
# Code for user input to create output table file #
###################################################

class TableFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.mdb = configs['summary_db']
        self.curdir = os.getcwd()
        self.entries = input_form.DefaultValueForm([('Name of output file',''),
                ('Location',self.curdir)], self,
                [('Choose Directory', self.onChoose, {'side':RIGHT})]) # buttons
        self.summary = gui_util.ComboBoxFrame(self,
                choices=list(self.mdb.list_entries()),
                labeltext='Summary to output table name for')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, fill=X)

        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.onClose)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onClose, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

    def onClose(self):
        """Closes dbs and destroys window"""
        self.parent.destroy()

    def onSubmit(self):
        """Gets information to generate a writer object and write info"""
        for row in self.entries.row_list:
            if row.label_text == 'Name of output file':
                name = row.entry.get()
            else: # other row
                outdir = row.entry.get()
        sname = self.summary.selected.get()
        sobj = self.mdb[sname]
        # now check for file details
        if name == '': # user did not enter value
            name = sname + '_summary_table.csv'
        else:
            if not name.endswith('.csv'):
                name = name + '.csv'
        outpath = os.path.join(outdir,name)
        if os.path.exists(outpath):
            pass # freak out
        fobj = open(outpath,'w') # open file for writing
        # Finally, instantiate the required object and run it
        writer = summary_writer.ResultSummaryWriter(sobj, fobj)
        writer.write()
        self.onClose()

#############################################
# Code for getting sequences from summaries #
#############################################

class SummarySeqFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.parent = parent
        self.mdb = configs['summary_db']
        self.params = SummSeqParamFrame(self)
        # toolbar and buttons
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)
        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onCancel(self):
        self.parent.destroy()

    def onSubmit(self):
        """Calls to get sequences and closes window"""
        name,location,summ_name,hit_types,modes,extras = self.params.get_params()
        sum_writer = seqs_from_summary.SummarySeqWriter(
                basename = name,
                summary_obj = self.mdb[summ_name],
                target_dir = location,
                hit_type = hit_types,
                mode = modes,
                extra_groups = extras)
        sum_writer.run()
        self.parent.destroy()

class SummSeqParamFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.pack()
        self.mdb = configs['summary_db']
        self.curdir = os.getcwd()
        self.entries = input_form.DefaultValueForm(
                [('Basename',''),('Location',self.curdir)],
                self,
                [('Choose Directory', self.onChoose, {'side':RIGHT})])
        self.summ_name = gui_util.ComboBoxFrame(self,
                choices = list(self.mdb.list_entries()),
                labeltext='Summary to use')
        self.hit_type = gui_util.ComboBoxFrame(self,
            choices = ['All','Positive only','Tentative only','Unlikely only',\
            'Positive and Tentative','Positive and Unlikely','Tentative and Unlikely'],
            labeltext='Type of sequences to write')
        self.mode = gui_util.ComboBoxFrame(self,
            choices = ['Both','Combine all DBs','By DB only'],
            labeltext='Main grouping of sequences')
        self.extra_groups = gui_util.CheckBoxGroup(self,
            labels = ['By Supergroup','By Strain'],
            labeltext='Additional groups of sequences')

    def onChoose(self):
        """Pops up a directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # clear first
                entry_row.entry.insert(0,dirpath)

    def get_params(self):
        """Returns three lists of params to parent widget"""
        hit_types = []
        modes = []
        extras = []
        try:
            name = self.entries.get('Basename')
            location = self.entries.get('Location')
            sname = self.summ_name.get()
            for val in (name,location,sname):
                if val == '' or val is None:
                    raise ValueError
            # deal with hit_types first
            hit_type = self.hit_type.get()
            if hit_type == '': # nothing was selected
                raise ValueError
            if hit_type == 'All':
                hit_types.extend(['positive','tentative','unlikely'])
            elif hit_type == 'Positive only':
                hit_types.append('positive')
            elif hit_type == 'Tentative only':
                hit_types.append('tentative')
            elif hit_type == 'Unlikely only':
                hit_types.append('unlikely')
            elif hit_type == 'Positive and Tentative':
                hit_types.extend(['positive','tentative'])
            elif hit_type == 'Positive and Unlikely':
                hit_types.extend(['positive','unlikely'])
            elif hit_type == 'Tentative and Unlikely':
                hit_types.extend(['tentative','unlikely'])
            # now deal with mode
            mode = self.mode.get()
            if mode == '': # nothing was selected
                raise ValueError
            if mode == 'Both':
                modes.extend(['all','db'])
            elif mode == 'Combine all DBs':
                modes.append('all')
            elif mode == 'By DB only':
                modes.append('db')
            # finally, deal with any extras
            extra_dict = self.extra_groups.get()
            for k,v in extra_dict.items():
                if k == 'By Supergroup' and v:
                    extras.append('supergroup')
                elif k == 'By Strain' and v:
                    extras.append('strain')
            return name,location,sname,hit_types,modes,extras
        except ValueError:
            messagebox.showwarning('Summary Seq Window',
                    'Missing one or more required options')
