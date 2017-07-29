"""
Implements non-blocking search operation(s) in a separate non-modal window
that tracks progress while searches are running. For each search that finishes,
the main thread updates the progress bar to provide the user with an
indication of overall progress.
"""

from tkinter import *
from tkinter import ttk
import threading, queue

from searches.blast import blast_setup
from results import result_obj

blast_path = '/usr/local/ncbi/blast/bin'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class ProgressFrame(Frame):
    def __init__(self, search_list, callback=None,
        callback_args=None, parent=None):
        Frame.__init__(self, parent)
        self.pack()
        self.search_list = search_list # list with objects and args
        self._length = len(self.search_list)
        self.queue = queue.Queue()
        self.robjs = [] # initialize and empty list
        self.callback = callback
        self.callback_args = callback_args
        self.parent = parent

        # Make non-modal, i.e. un-closeable
        self.parent.protocol('WM_DELETE_WINDOW', lambda: None)

        # Code to add progress bar
        self.pvar = IntVar()
        self.pvar.set(0) # initial progress is zero
        self.p = ttk.Progressbar(self, # parent
                orient = HORIZONTAL,
                length = 100,
                mode = 'determinate', # specifies a set number of steps
                variable = self.pvar, # tied to variable for auto updates
                maximum = len(self.search_list))
        self.p.pack()

    def run(self):
        """Instantiates the thread consumer/queue and calls the thread"""
        # Invoke a non-blocking thread parallel to GUI
        threading.Thread(target = self._run).start()
        self.thread_consumer()

    def _run(self):
        """Function called by the thread, runs each BLAST search"""
        for sobj,qid,db,qobj,dbf,outpath,rdb,rid in self.search_list:
            if sobj.algorithm == 'blast':
                if sobj.q_type == 'protein' and sobj.db_type == 'protein':
                    blast_search = blast_setup.BLASTp(blast_path, qobj,
                        dbf, outpath)
                    blast_search.run_from_stdin()
            robj = result_obj.Result(rid, sobj.algorithm,
            sobj.q_type, sobj.db_type, qid, db, sobj.name, outpath)
            self.queue.put(robj) # indicates success

    def thread_consumer(self):
        """Checks the queue regularly for new results"""
        try:
            new_robj = self.queue.get(block=False)
            self.robjs.append(new_robj)
            curr_val = self.pvar.get()
            curr_val += 1
            self.pvar.set(curr_val)
        except(queue.Empty): # nothing to grab
            self.after(250, self.thread_consumer)
        else: # when finished
            if self.callback:
                self.callback_args = self.robjs
                self.callback(*self.callback_args)
            self.parent.destroy()
