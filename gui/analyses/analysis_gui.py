"""
This module contains code for GUI windows related to analyses in Goat.
"""

import os
from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from gui.util import gui_util, input_form
from gui.searches import search_gui
from searches import search_obj
from analyses import reciprocal_blast

class AnalysisPicker(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.analysis = gui_util.ComboBoxFrame(self, ['Reciprocal BLAST',
            'Reciprocal HMMer BLAST', 'Full BLAST and HMMer',
            'Iterative HMMer'], 'Please choose an analysis')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Pop up appropriate window for analysis to be performed"""
        choice = self.analysis.selected.get()
        if choice == 'Reciprocal BLAST':
            window = Toplevel()
            ReciprocalBLASTFrame(window)
            self.parent.destroy()
        elif choice == 'Reciprocal HMMer BLAST':
            pass
        elif choice == 'Full BLAST and HMMer':
            pass
        elif choice == 'Iterative HMMer':
            pass
        else: # nothing chosen
            pass # freak out

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

class ReciprocalBLASTFrame(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.search = RecipBLASTGui(self)
        self.sdb = configs['search_db']
        self.pack(expand=YES, fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Run', self.onRun, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRun(self):
        """Collect all relevant information and call reciprocal BLAST"""
        params = self.search.param_frame
        queries = self.search.query_frame.querybox
        dbs = self.search.db_frame.db_box
        for row in params.entries.row_list:
            if row.label_text == 'Forward search name':
                fwd_name = row.entry.get()
            elif row.label_text == 'Reverse search name':
                rev_name = row.entry.get()
            elif row.label_text == 'Location':
                location = row.entry.get()
        if params.keep_output.checked.get() == 0:
            ko = False
        else:
            ko = True
        fwd_sobj = search_obj.Search( # be explicit for clarity here
            name = fwd_name,
            algorithm = 'blast',
            q_type = params.q_type.selected.get(),
            db_type = params.db_type.selected.get(),
            queries = queries.item_list, # equivalent to all queries
            databases = dbs.item_list, # equivalent to all dbs
            keep_output = ko,
            output_location = location)
        # store search object in database
        #self.sdb[sname] = fwd_sobj # should eventually make a check that we did actually select something!
        # now run the search and parse the output
        recip_blast = reciprocal_blast.ReciprocalBLAST(fwd_name, fwd_sobj,
                rev_name, threaded=True)
        recip_blast.run()
        # Can destroy once run starts
        self.parent.destroy()

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

class RecipBLASTGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']
        self.param_frame = ReciprocalBLASTParams(self)
        self.query_frame = search_gui.QuerySummaryFrame(self.qdb, self)
        self.db_frame = search_gui.DatabaseSummaryFrame(self.rdb, self)
        self.add(self.param_frame)
        self.add(self.query_frame)
        self.add(self.db_frame)
        self.pack(expand=YES, fill=BOTH)

class ReciprocalBLASTParams(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.curdir = os.getcwd()
        self.entries = input_form.DefaultValueForm([('Forward search name',''),
                ('Reverse search name',''), ('Location',self.curdir)],
                self, [('Choose Directory', self.onChoose, {'side':RIGHT})])
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

