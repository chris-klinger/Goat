"""
Module containing code for setting up scrollsaw analyses.

At first, this will just be from summaries, but eventually would like to add an
interface to perform the analysis using any arbitrary input files.
"""

import os
from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from gui.util import gui_util,input_form
from util.sequences import scrollsaw

class ScrollSawFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack()
        self.input_type = gui_util.ComboBoxFrame(self,
                ['By Summary','Raw Files'])
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onSubmit(self):
        """Pop up appropriate window for analysis"""
        choice = self.input_type.selected.get()
        if choice == 'By Summary':
            window = Toplevel()
            SummScrollSawFrame(window)
            self.onCancel()

    def onCancel(self):
        self.parent.destroy()

class SummScrollSawFrame(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.mdb = configs['summary_db']
        self.pack()
        self.curdir = os.getcwd()
        self.params = input_form.DefaultValueForm(
            [('Basename',''),('Number of Seqs',''),('Location',self.curdir)],
            self, [('Choose Directory',self.onChoose,{'side':RIGHT})])
        self.summ_id = gui_util.ComboBoxFrame(self,
                choices = list(self.mdb.list_entries()),
                labeltext='Summary to Use')
        self.group = gui_util.RadioBoxFrame(self,
                choices = [('Supergroup','supergroup'),('Strain','strain')],
                labeltext='Group to Select Sequence For')
        self.toolbar = Frame(self)
        self.toolbar.pack(side=BOTTOM, expand=YES, fill=X)

        self.buttons = [('Done', self.onSubmit, {'side':RIGHT}),
                        ('Cancel', self.onCancel, {'side':RIGHT})]
        for (label, action, where) in self.buttons:
            Button(self.toolbar, text=label, command=action).pack(where)

    def onChoose(self):
        """Generic file choice"""
        dirpath = filedialog.askdirectory()
        for entry_row in self.entries.row_list:
            if entry_row.label_text == 'Location':
                entry_row.entry.delete(0,'end') # delete previous entry first
                entry_row.entry.insert(0,dirpath)

    def onSubmit(self):
        """Get params, create object, and run it"""
        ssaw = scrollsaw.SummaryScrollSaw(
                basename = self.params.get('Basename'),
                summary_obj = self.mdb[self.summ_id.get()],
                target_dir = self.params.get('Location'),
                sort_group = self.group.get(),
                num_seqs = self.params.get('Number of Seqs'))
        ssaw.run()
        self.onCancel()

    def onCancel(self):
        self.parent.destroy()
