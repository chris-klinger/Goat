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
    def __init__(self, algorithm, search_list, callback=None,
        callback_args=None, parent=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.algorithm = algorithm
        self.search_list = search_list # list with objects and args
        self.num_todo = len(search_list)
        self.num_finished = 0
        self.callback = callback
        self.callback_args = callback_args

        # Make non-modal, i.e. un-closeable
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', lambda: None)

        # Add some information
        Label(self, text='Searching for queries using {}'.format(self.algorithm)).pack()

        # Code to add progress bar, update 'value' attr after each search
        self.p = ttk.Progressbar(self, # parent
                orient = HORIZONTAL,
                length = 200,
                mode = 'determinate', # specifies a set number of steps
                maximum = len(self.search_list))
        self.p.pack()

        # Add another label that can be modified on each search
        self.search_label = Label(self, text='Performing search {} of {}'.format(
            self.num_finished, self.num_todo), anchor='center', justify='center')
        self.search_label.pack(side=BOTTOM, expand=YES)

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
            self.num_finished += 1
        self.queue.put(robjs) # indicates success

    def thread_consumer(self):
        """Checks the queue regularly for new results"""
        # Even if there are no results to grab, update status bar each time
        self.p['value'] = self.num_finished
        self.search_label['text'] = 'Performing search {} of {}'.format(
            self.num_finished, self.num_todo)
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
