"""
Implements non-blocking search operation(s) in a separate non-modal window
that tracks progress while searches are running. For each search that finishes,
the main thread updates the progress bar to provide the user with an
indication of overall progress.
"""

from tkinter import *
from tkinter import ttk
import threading, queue
#import time

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

        # start producer thread, consumer loop
        self.queue = queue.Queue()
        threading.Thread(target=self._run).start()
        self.thread_consumer()

    def _run(self):
        """Function called by the thread, runs each BLAST search"""
        robjs = []
        for sobj,qid,db,qobj,dbf,outpath,rdb,rid in self.search_list:
            if sobj.algorithm == 'blast':
                if sobj.q_type == 'protein' and sobj.db_type == 'protein':
                    blast_search = blast_setup.BLASTp(blast_path, qobj,
                        dbf, outpath)
                    blast_search.run_from_stdin()
            robj = result_obj.Result(rid, sobj.algorithm,
                sobj.q_type, sobj.db_type, qid, db, sobj.name, outpath)
            robjs.append(robj)
            curr_val = self.pvar.get()
            curr_val += 1
            self.pvar.set(curr_val)
        self.queue.put(robjs) # indicates success

    def thread_consumer(self):
        """Checks the queue regularly for new results"""
        #while not len(self.robjs) == self._length: # still BLAST results to get
        try:
            #print('trying')
            robjs = self.queue.get(block=False)
        except(queue.Empty): # nothing to grab
            #print('got nothing')
            self.after(200, self.thread_consumer)
        # when finished
        else:
            #print("calling else block")
            if self.callback:
                self.callback(*robjs)
            self.parent.destroy()
