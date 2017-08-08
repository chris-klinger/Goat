"""
This module contains code for running a full reciprocal BLAST analysis in Goat,
including running the forward search, parsing the output and getting the
intermediate queries, running the reverse search, parsing the output, and then
summarizing the results of both the forward and reverse search.
"""

from tkinter import *
#from tkinter import ttk
import threading

from bin.initialize_goat import configs

from searches import search_runner, search_obj
from results import intermediate

class ReciprocalBLAST:
    def __init__(self, fwd_name, fwd_sobj, rev_name, threaded=False, gui=None):
        self.fwd_name = fwd_name
        self.fwd_sobj = fwd_sobj
        self.rev_name = rev_name
        self.threaded = threaded
        self.gui = gui
        self.rdb = configs['record_db']
        self.qdb = configs['query_db']
        self.udb = configs['result_db']
        self.sdb = configs['search_db']

    def run(self):
        """
        Calls all necessary steps; if threaded, pops up a new window that tracks
        progress of both searches and runs as a separate thread to that of the
        main GUI program; otherwise main GUI hangs until completion.
        """
        if self.threaded:
            window = Toplevel()
            runner = search_runner.SearchRunner(self.fwd_name, self.fwd_sobj, self.qdb,
                    self.rdb, self.udb, self.sdb, mode='new', threaded=True, gui=window,
                    no_win=False, # don't destroy popup on first search
                    owidget=self) # break up search into new and old
            self.frame = RecipBLASTFrame('Running reciprocal BLAST analysis',
                    self.fwd_sobj, runner, self.qdb, self.rdb, self.udb, self.sdb,
                    self.rev_name, self.threaded, window)
            self.frame.run()
        else:
            pass # non-threaded version

    def _cont(self):
        """Signal to RecipBLASTFrame to continue with rev searches"""
        self.frame.cont()

class RecipBLASTFrame(Frame):
    def __init__(self, label, fwd_sobj, fwd_search_runner, qdb, rdb, udb, sdb,
            rev_name, threaded=False, parent=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.pack(expand=YES, fill=BOTH)
        Label(self, text=label).pack()
        self.fwd_sobj = fwd_sobj
        self.fwd = fwd_search_runner
        self.qdb = qdb
        self.rdb = rdb
        self.udb = udb
        self.sdb = sdb
        self.rev_name = rev_name
        self.threaded = threaded

    def run(self):
        """actually run the search"""
        threading.Thread(target=self._run).start()

    def _run(self):
        """
        Begins runnig the forward search, then parses the output and sets up reverse search
        before running that search as well.
        """
        print('running forward search')
        self.fwd.run()

    def cont(self):
        """
        Parses output from forward search into new queries and runs reverse search.
        """
        intermediate.Search2Queries( # now get the reverse queries
            self.fwd_sobj, self.udb, self.qdb, self.rdb).populate_search_queries()
        # Now get all needed queries
        print('getting reverse queries')
        queries = []
        for uid in self.fwd_sobj.list_results(): # result ids
            #print(uid)
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                #print('\t' + str(qid))
                queries.append(qid)
        rev_sobj = search_obj.Search( # be explicit for clarity here
            name = self.rev_name,
            algorithm = self.fwd_sobj.algorithm,
            q_type = self.fwd_sobj.db_type, # queries here are the same as the forward db type
            db_type = self.fwd_sobj.q_type, # conversely, db is the original query type
            queries = queries, # equivalent to all queries
            databases = [], # reverse search, so target_db is on each query!
            keep_output = self.fwd_sobj.keep_output,
            output_location = self.fwd_sobj.output_location)
        # store search object in database
        #self.sdb[sname] = rev_sobj # should eventually make a check that we did actually select something!
        # now run the search and parse the output
        runner = search_runner.SearchRunner(self.rev_name, rev_sobj, self.qdb, self.rdb, self.udb,
                self.sdb, mode='old', fwd_search=self.fwd_sobj, threaded=self.threaded, gui=self.parent)
        print('running reverse search')
        runner.run()

