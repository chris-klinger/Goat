"""
This module contains code for a user interface to summarizing results in Goat.
User is asked to choose between one or two searches to summarize, and then
depending on this choice to fill in different forms for relevant information.
"""

from tkinter import *
from tkinter import ttk

from gui.util import gui_util, input_form
from summaries import summary_obj, summarizer

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
            ['Next hit evalue',0.05],['Max forward hits',10],
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
        print(fwd_search)
        fwd_sobj = self.sdb[fwd_search]
        rev_search = self.rev_search.selected.get()
        print(rev_search)
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
        print('\n' + str(sum_obj))
        for qid in sum_obj.queries:
            print('\t' + qid)
            qobj = sum_obj.fetch_query_summary(qid)
            for uid in qobj.db_list:
                print('\t\t' + uid)
                uobj = qobj.fetch_db_summary(uid)
                for hit in uobj.positive_hit_list:
                    print('\t\t\t' + str(hit))
        #self.mdb.add_entry(name, sum_obj)
        #self.mdb.commit()
        self.onClose()

