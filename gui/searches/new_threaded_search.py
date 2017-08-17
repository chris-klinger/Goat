"""
This module contains updated code for providing user updates on searches in Goat.
Not sure if this will work properly without threading, but will try; either way,
trying to separate user information for searches from the search itself, and
provide a better way to feed back the callback from a search to the main GUI
regardless of whether or not threading is used.
"""

import threading, queue

from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from searches import new_search_runner

blast_path = '/usr/local/ncbi/blast/bin'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class ProgressFrame(Frame):
    def __init__(self, starting_sobj, mode, parent=None, threaded=True,
            other_widget=None, callback=None, callback_args=None):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.start_sobj = starting_sobj
        self.mode = mode
        self.threaded = threaded
        self.other = other_widget
        self.callback = callback
        self.callback_args = callback_args

        # Make non-modal, i.e. un-closeable
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', lambda: None)

        # Add some information, keep a ref to change the text later
        self.search_info = Label(self, text='Searching for queries using {}'.format(
            self.start_sobj.algorithm), anchor='center', justify='center')
        self.search_info.pack(expand=YES)

        # Determine the maximum number of searches to do
        self.num_todo = self.determine_max_searches(self.start_sobj, mode)
        # Code to add progress bar, update 'value' attr after each search
        self.p = ttk.Progressbar(self, # parent
                orient = HORIZONTAL,
                length = 200,
                mode = 'determinate', # specifies a set number of steps
                maximum = self.num_todo)
        self.p.pack()
        # Default starting value for the search bar
        self.num_finished = 1 # don't index from zero, first search is number 1

        # Add another label to report hard numbers in progress bar
        self.search_label = Label(self, text='Performing search {} of {}'.format(
            self.num_finished, self.num_todo), anchor='center', justify='center')
        self.search_label.pack(side=BOTTOM, expand=YES)

    def run(self):
        """start producer thread, consumer loop"""
        if self.threaded:
            configs['threads'].add_thread()
            # always create the queue
            self.queue = queue.Queue()
            if self.mode == 'racc':
                threading.Thread(target=self._run_racc_blast).start()
            elif self.mode == 'new':
                threading.Thread(target=self._run_fwd_search).start()
            elif self.mode == 'rev':
                threading.Thread(target=self._run_rev_search).start()
            # always start the thread consumer function
            self.thread_consumer()
        else:
            pass

    def _run_racc_blast(self):
        """Runs blast searches for raccs, and then removes all info after"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='racc',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done') # signal completion

    def _run_fwd_search(self):
        """Function called by the thread, runs each BLAST search"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='new',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def _run_rev_search(self):
        """Calls Search Runner for reverse searches"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='rev',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def thread_consumer(self):
        """Checks the queue regularly for new results"""
        # Even if there are no results to grab, update status bar each time
        self.p['value'] = self.num_finished
        self.search_label['text'] = 'Performing search {} of {}'.format(
            self.num_finished, self.num_todo)
        try:
            done = self.queue.get(block=False)
        except(queue.Empty): # nothing to grab
            self.after(200, self.thread_consumer)
        # when finished
        else:
            if done:
                if self.callback:
                    if self.callback_args:
                        self.callback(*self.callback_args)
                    else:
                        self.callback()
            self.parent.destroy()

    def increment_search_count(self):
        """Increments counter after each search finishes"""
        #print("incrementing counter")
        self.num_finished += 1

    def determine_max_searches(self, sobj, mode):
        """Determines the number of searches to run"""
        if mode == 'racc':
            return len(sobj.queries)
        elif mode == 'new':
            return (len(sobj.queries) * len(sobj.databases))
        elif mode == 'rev':
            return len(sobj.queries)
