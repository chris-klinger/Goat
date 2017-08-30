"""
This module contains code for GUI windows related to analyses in Goat.
"""

import os
from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from gui.util import gui_util, input_form
from gui.searches import search_gui, new_threaded_search
from searches import search_obj

#####################################################
# Code for choosing the kind of analysis to perform #
#####################################################

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
            window = Toplevel()
            HMMerBLASTFrame(window)
            self.parent.destroy()
        elif choice == 'Full BLAST and HMMer':
            window = Toplevel()
            FullBLASTHMMerFrame(window)
            self.parent.destroy()
        elif choice == 'Iterative HMMer':
            pass
        else: # nothing chosen
            pass # freak out

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

###############################################################
# Code for setting up and running a reciprocal BLAST analysis #
###############################################################

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
        fwd_name,rev_name,location,fwd_qtype,fwd_dbtype,fwd_ko,rev_ko = params.get_current_values()
        queries = self.search.query_frame.querybox
        dbs = self.search.db_frame.db_box
        fwd_sobj = search_obj.Search( # be explicit for clarity here
            name = fwd_name,
            algorithm = 'blast',
            q_type = fwd_qtype,
            db_type = fwd_dbtype,
            queries = queries.item_list, # equivalent to all queries
            databases = dbs.item_list, # equivalent to all dbs
            keep_output = fwd_ko,
            output_location = location)
        # store fwd search object in database
        # should eventually make a check that we did actually select something!
        self.sdb.add_entry(fwd_name, fwd_sobj)
        # now run the search and parse the output
        window = Toplevel()
        prog_frame = new_threaded_search.ProgressFrame(
                fwd_sobj, 'recip_blast', window, other_widget=self,
                callback=self.recip_blast_callback,
                rev_search_name=rev_name, keep_rev_output=rev_ko)
        prog_frame.run()
        # Can destroy once run starts
        self.onCancel()

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

    def recip_blast_callback(self):
        """Commit changes in multiple databases"""
        configs['threads'].remove_thread()
        configs['search_queries'].commit()
        configs['search_db'].commit()
        configs['result_db'].commit()

class RecipBLASTGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = ReciprocalBLASTParams(self)
        self.query_frame = search_gui.QuerySummaryFrame(self,
                algorithm='blast') # must set algorithm or interface blocks
        self.db_frame = search_gui.DatabaseSummaryFrame(self)
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
        self.entries = input_form.DefaultValueForm(
                [('Forward search name','fwd1'),('Reverse search name','rev1'), ('Location',self.curdir)],
                self, [('Choose Directory', self.onChoose, {'side':RIGHT})])
        self.q_type = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Query data type')
        self.db_type = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Target data type')
        self.fwd_ko = gui_util.CheckBoxFrame(
                self, 'Keep forward search output files?')
        self.rev_ko = gui_util.CheckBoxFrame(
                self, 'Keep reverse search output files?')

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

    def get_current_values(self):
        """Returns all current values"""
        return (self.entries.get('Forward search name'),
                self.entries.get('Reverse search name'),
                self.entries.get('Location'),
                self.q_type.get(),
                self.db_type.get(),
                self.fwd_ko.button_checked(),
                self.rev_ko.button_checked())

##################################################################
# Code for setting up and running a fwd HMMer/rev BLAST analysis #
##################################################################

class HMMerBLASTFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.search = HMMerBLASTGui(self)
        self.sdb = configs['search_db']
        self.pack(expand=YES, fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Run', self.onRun, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRun(self):
        """Collect all relevant information and call fwd HMMer followed by rBLAST"""
        params = self.search.param_frame
        (fwd_name,rev_name,location,rev_record,\
            fwd_qtype,fwd_dbtype,fwd_ko,rev_ko) = params.get_current_values()
        queries = self.search.query_frame.querybox
        dbs = self.search.db_frame.db_box
        fwd_sobj = search_obj.Search( # be explicit for clarity here
            name = fwd_name,
            algorithm = 'hmmer',
            q_type = fwd_qtype,
            db_type = fwd_dbtype,
            queries = queries.item_list, # equivalent to all queries
            databases = dbs.item_list, # equivalent to all dbs
            keep_output = fwd_ko,
            output_location = location,
            rev_record = rev_record)
        # store fwd search object in database
        # should eventually make a check that we did actually select something!
        self.sdb.add_entry(fwd_name, fwd_sobj)
        # now run the search and parse the output
        window = Toplevel()
        prog_frame = new_threaded_search.ProgressFrame(
                fwd_sobj, 'hmmer_blast', window, other_widget=self,
                callback=self.hmmer_blast_callback,
                rev_search_name=rev_name, keep_rev_output=rev_ko)
        prog_frame.run()
        # Can destroy once run starts
        self.onCancel()

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

    def hmmer_blast_callback(self):
        """Commit changes in multiple databases"""
        configs['threads'].remove_thread()
        configs['search_queries'].commit()
        configs['search_db'].commit()
        configs['result_db'].commit()

class HMMerBLASTGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = HMMerBLASTParams(self)
        self.query_frame = search_gui.QuerySummaryFrame(self,
                algorithm='hmmer') # must set algorithm or interface blocks
        self.db_frame = search_gui.DatabaseSummaryFrame(self)
        self.add(self.param_frame)
        self.add(self.query_frame)
        self.add(self.db_frame)
        self.pack(expand=YES, fill=BOTH)

class HMMerBLASTParams(Frame):
    def __init__(self, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.curdir = os.getcwd()
        self.rdb = configs['record_db']
        self.entries = input_form.DefaultValueForm(
                [('Forward search name',''),('Reverse search name',''), ('Location',self.curdir)],
                self, [('Choose Directory', self.onChoose, {'side':RIGHT})])
        self.rev_record = gui_util.ComboBoxFrame(self,
                choices = list(self.rdb.list_entries()),
                labeltext='Record to use for reverse searches')
        self.q_type = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Query data type')
        self.db_type = gui_util.RadioBoxFrame(self,
                [('Protein','protein'), ('Genomic','genomic')],
                labeltext='Target data type')
        self.fwd_ko = gui_util.CheckBoxFrame(
                self, 'Keep forward search output files?')
        self.rev_ko = gui_util.CheckBoxFrame(
                self, 'Keep reverse search output files?')

    def onChoose(self):
        """Pops up directory choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

    def get_current_values(self):
        """Returns all current values"""
        return (self.entries.get('Forward search name'),
                self.entries.get('Reverse search name'),
                self.entries.get('Location'),
                self.rev_record.get(),
                self.q_type.get(),
                self.db_type.get(),
                self.fwd_ko.button_checked(),
                self.rev_ko.button_checked())

#############################################################
# Code for setting up and running full BLAST/HMMer analysis #
#############################################################

class FullBLASTHMMerFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.search = FullBLASTGui(self)
        self.sdb = configs['search_db']
        self.pack(expand=YES, fill=BOTH)
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Run', self.onRun, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onRun(self):
        """
        Sets up and runs a complete BLAST analysis. Summarizes the results based
        on e-value cutoff criteria and then uses all positive hits together with
        the original queries to create a new sequence file from which to build
        an MSA and subsequent HMM. This HMM is then used to search the query dbs
        again, and finally, a reverse BLAST is performed.
        """
        params = self.search.param_frame
        (fwd_name,rev_name,location,fwd_qtype,\
            fwd_dbtype,fwd_ko,rev_ko) = params.get_current_values()
        queries = self.search.query_frame.querybox
        dbs = self.search.db_frame.db_box
        # gather intermediate information into a dict
        keys = ('fwd_name','rev_name','summ_name','fwd_evalue','rev_evalue',
                'next_evalue','fwd_hits','rev_hits','fwd_ko','rev_ko')
        values = self.search.intermediate_frame.get_current_values()
        int_args = {}
        for k,v in zip(keys,values):
            int_args[k] = v
        fwd_sobj = search_obj.Search( # be explicit for clarity here
            name = fwd_name,
            algorithm = 'blast',
            q_type = fwd_qtype,
            db_type = fwd_dbtype,
            queries = queries.item_list, # equivalent to all queries
            databases = dbs.item_list, # equivalent to all dbs
            keep_output = fwd_ko,
            output_location = location)
        # store fwd search object in database
        # should eventually make a check that we did actually select something!
        self.sdb.add_entry(fwd_name, fwd_sobj)
        # now run the search and parse the output
        window = Toplevel()
        prog_frame = new_threaded_search.ProgressFrame(
                fwd_sobj, 'full_blast_hmmer', window, other_widget=self,
                callback=self.full_blast_hmmer_callback,
                rev_search_name=rev_name, keep_rev_output=rev_ko,
                **int_args) # use these as kwargs
        prog_frame.run()
        # Can destroy once run starts
        self.onCancel()

    def onCancel(self):
        """Close without doing anything"""
        self.parent.destroy()

    def full_blast_hmmer_callback(self):
        """Commit changes in multiple databases"""
        configs['threads'].remove_thread()
        configs['search_queries'].commit()
        configs['search_db'].commit()
        configs['result_db'].commit()
        configs['summary_db'].commit()

class FullBLASTGui(ttk.Panedwindow):
    def __init__(self, parent=None):
        ttk.Panedwindow.__init__(self, parent, orient=HORIZONTAL)
        self.parent = parent
        self.param_frame = ReciprocalBLASTParams(self)
        self.intermediate_frame = IntBLASTHMMerParams(self)
        self.query_frame = search_gui.QuerySummaryFrame(self,
                algorithm='blast') # must set algorithm or interface blocks
        self.db_frame = search_gui.DatabaseSummaryFrame(self)
        self.add(self.param_frame)
        self.add(self.intermediate_frame)
        self.add(self.query_frame)
        self.add(self.db_frame)
        self.pack(expand=YES, fill=BOTH)

class IntBLASTHMMerParams(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        Label(self, text='Intermediate HMMer/BLAST search',
                anchor='center', justify='center').pack()
        self.entries = input_form.DefaultValueForm(
                [('HMMer search name','hmmer'),('Reverse search name','rev2')],self)
        self.cutoffs = input_form.DefaultValueForm(
                [('Summary name','fullsumm'),('Minimum forward evalue','0.05'),
                ('Minimum reverse evalue','0.05'),('Next hit evalue','0.05'),
                ('Max forward hits','10'),('Max reverse hits','10')], self)
        self.fwd_ko = gui_util.CheckBoxFrame(
                self, 'Keep forward search output files?')
        self.rev_ko = gui_util.CheckBoxFrame(
                self, 'Keep reverse search output files?')

    def get_current_values(self):
        """Returns all current values"""
        return (self.entries.get('HMMer search name'),
                self.entries.get('Reverse search name'),
                self.cutoffs.get('Summary name'),
                float(self.cutoffs.get('Minimum forward evalue')),
                float(self.cutoffs.get('Minimum reverse evalue')),
                float(self.cutoffs.get('Next hit evalue')),
                int(self.cutoffs.get('Max forward hits')),
                int(self.cutoffs.get('Max reverse hits')),
                self.fwd_ko.button_checked(),
                self.rev_ko.button_checked())

