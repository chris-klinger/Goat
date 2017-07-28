"""
This module contains code for a user interface to summarizing results in Goat.
User is asked to choose between one or two searches to summarize, and then
depending on this choice to fill in different forms for relevant information.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util, input_form
from summaries import summary_obj, summarizer

################################
# Code for summarizing results #
################################

class SearchSummaryFrame(Frame):
    def __init__(self, summary_db, query_db, search_db, result_db, parent):
        Frame.__init__(self, parent)
        self.mdb = summary_db
        self.qdb = query_db
        self.sdb = search_db
        self.udb = result_db
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
        for db in self._dbs:
            db.close()
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
            db.close()
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
        summer = summarizer.SearchSummarizer(sum_obj,
                self.qdb, self.sdb, self.udb)
        summer.summarize_two_results()
        #print('\n' + str(sum_obj))
        #for qid in sum_obj.queries:
            #print('\t' + qid)
            #qobj = sum_obj.fetch_query_summary(qid)
            #for uid in qobj.db_list:
                #print('\t\t' + uid)
                #uobj = qobj.fetch_db_summary(uid)
                #for hit in uobj.positive_hit_list:
                    #print('\t\t\t' + str(hit))
        self.mdb.add_entry(name, sum_obj)
        self.mdb.commit()
        self.onClose()

##############################
# Code for viewing summaries #
##############################

class SummaryFrame(Frame):
    def __init__(self, summary_db, result_db, parent=None):
        Frame.__init__(self, parent)
        self.mdb = summary_db
        self.udb = result_db
        self.parent = parent
        self.summaries = SummaryGui(summary_db, result_db, self)
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
        self.mdb.close()
        self.udb.close()
        self.parent.destroy()

    def onRemove(self):
        """Removes a summary object and all associated sub-objects. Removal should
        be by whole summary, not individual sub-objects, and in fact, perhaps may
        make this an illegal operation?"""
        item_name = self.results.result_tree.focus()
        item = self.results.result_tree.item(item_name)
        if item['tags'][0] == 'summary':
            self.mdb.remove_entry(item['text'])
        else: # do we want to allow removal of anything other than summaries?
            pass
        self.summaries.summary_tree.update() # lastly, call for an update

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
        self.summary_tree = SummaryTree(summary_db, result_db, self.info_frame, self)
        self.add(self.summary_tree)
        self.add(self.info_frame)
        self.pack(expand=YES, fill=BOTH)

class SummaryTree(ttk.Treeview):
    def __init__(self, summary_db, result_db, other_widget, parent=None):
        ttk.Treeview.__init__(self, parent)
        self.mdb = summary_db
        self.udb = result_db
        self.info = other_widget
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
        for summary in self.mdb.list_entries():
            mobj = self.mdb[summary]
            self.insert('','end',mobj,text=summary,tags=('summary'))
            for qid in mobj.query_list:
                qobj = mobj.queries[qid]
                self.insert(mobj,'end',qobj,text=qid,tags=('querysum'))
                for db in qobj.db_list:
                    dbobj = qobj.dbs[db]
                    self.insert(qobj,'end',dbobj,text=db,tags=('dbsum'))
                    for hitlist in dbobj.lists:
                        lobj = getattr(dbobj,hitlist)
                        if not len(lobj) == 0: # don't care about empty lists
                            self.insert(dbobj,'end',lobj,text=hitlist,tags=('hitlist'))
                            for hit in lobj: # object here is a simple list
                                hobj = dbobj.hits[hit]
                                self.insert(lobj,'end',hobj,text=hit,tags=('hit'))

    def itemClicked(self, tag):
        """Builds a list of information for display by ResultInfo panel for
        either searches or results; delegates formatting/display to panel"""
        item_name = self.focus() # here item should be the object itself?
        item = self.item(item_name)
        parent_list = self.get_ancestors(item_name,[])
        db_obj = self.get_item_from_db(parent_list, self.mdb)
        if tag == 'summary':
            #print(db_obj)
            mlist = []
            # Add forward information
            mlist.extend([item['text'], len(db_obj.query_list),
                db_obj.fwd, db_obj.fwd_qtype, db_obj.fwd_dbtype,
                db_obj.fwd_algorithm, db_obj.fwd_evalue, db_obj.fwd_max_hits])
            # Add reverse information, if present
            if db_obj.rev: # not None, there is reverse stuff
                mlist.extend([db_obj.rev, db_obj.rev_qtype, db_obj.rev_dbtype,
                    db_obj.rev_algorithm, db_obj.rev_evalue, db_obj.rev_max_hits])
            # Add evalue and max cutoff information
            mlist.append(db_obj.next_evalue)
            self.info.update_info('summary', *mlist)
        elif tag == 'querysum':
            qlist = []
            qlist.extend([item['text'], len(db_obj.db_list)])
            self.info.update_info('querysum', *qlist)
        elif tag == 'dbsum':
            dlist = []
            dlist.extend([item['text'], db_obj.status])
            self.info.update_info('dbsum', *dlist)
        elif tag == 'hitlist':
            tlist = []
            name = item['text']
            if name == 'positive_hit_list':
                status = 'positive'
            elif name == 'tentative_hit_list':
                status = 'tentative'
            else: # unlikely
                status = 'unlikely'
            tlist.extend([status, len(db_obj)])
            self.info.update_info('hitlist', *tlist)
        elif tag == 'hit':
            print(tag)
            print(db_obj)
            for k,v in db_obj.__dict__.items():
                print(str(k) + ' ' + str(v))
            hlist = []
            hlist.extend([db_obj.fwd_id, db_obj.fwd_evalue])
            if db_obj.pos_rev_id: # not None
                hlist.extend([db_obj.pos_rev_id, db_obj.pos_rev_evalue,
                    db_obj.neg_rev_id, db_obj.neg_rev_evalue,
                    db_obj.rev_evalue_diff])
            hlist.append(db_obj.status)
            self.info.update_info('hit', *hlist)

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
        elif index == 3:
            new_obj = getattr(obj,item) # lists
        else:
            new_obj = db_obj.hits[item] # go back to ResultSummary for actual hit
        if len(item_list) == 1: # only one item remaining
            return new_obj
        else:
            item_list.remove(item)
            index += 1
            return self.get_item_from_db(item_list, new_obj, index, db_obj) # recur

class ResultInfo(ttk.Label):
    def __init__(self, parent=None):
        ttk.Label.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.displayInfo = StringVar()
        self.config(textvariable = self.displayInfo,
                width=-75,
                anchor='center', justify='center')
        self.displayInfo.set('')

    def update_info(self, display_type, *values):
        """Displays information on either searches or results"""
        display_string = ''
        if display_type == 'summary':
            display_string += ('Summary Information: \n\n\n')
            labels = ['Summary Name: ', 'Number Queries: ', 'Forward Search: ',
                    'Forward Query Type: ', 'Forward Database Type: ',
                    'Forward Search Algorithm: ', 'Forward E-value cutoff: ',
                    'Forward Hit Number Cutoff: ']
            if len(values) > 8:
                labels.extend(['Reverse Search: ', 'Reverse Query Type: ',
                    'Reverse Database Type: ', 'Reverse Search Algorithm: ',
                    'Reverse E-value cutoff: ', 'Reverse Hit Number Cutoff: '])
            labels.append('Next Hit Evalue Cutoff: ')
        elif display_type == 'querysum':
            display_string += ('Query Information: \n\n\n')
            labels = ['Query Name: ', 'Number of Databases Searched In: ']
        elif display_type == 'dbsum':
            display_string += ('Database Information: \n\n\n')
            labels = ['Database Name: ', 'Status of Searches in Database: ']
        elif display_type == 'hitlist':
            display_string += ('Hit Group Information: \n\n\n')
            labels = ['Hit status(es): ', 'Number of Hits: ']
        elif display_type == 'hit':
            display_string += ('Hit Information: \n\n\n')
            labels = ['Forward Query ID: ', 'Forward Evalue: ']
            if len(values) > 3:
                labels.extend(['First Positive Reverse Hit ID: ',
                    'First Positive Reverse Hit Evalue: ',
                    'First Negative Reverse Hit ID: ',
                    'First Negative Reverse Hit Evalue: ',
                    'Reverse Hits Evalue Difference: '])
            labels.append('Hit Status')
        for l,v in zip(labels,values):
            display_string += (l + str(v) + '\n')
        self.displayInfo.set(display_string)

