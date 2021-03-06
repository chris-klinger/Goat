"""
This module contains code to actually perform searches in Goat. Idea is to take a
search object, and pointers to the query, record, and results databases. Using the
information in the search object, each query/database search is ran and used to
generate a new results object in the results db. Each result object is also added
to the search object in order to keep track of which results belong to which
search.
"""

import os

from tkinter import *
from Bio.Blast import NCBIXML

from bin.initialize_goat import configs

from searches.blast import blast_setup
from searches.hmmer import hmmer_setup, hmmer_parser
from results import result_obj

from gui.searches import threaded_search

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'
hmmer_path = '/Users/cklinger/src/hmmer-3.1b1-macosx-intel/src'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class SearchRunner:
    """Actually runs searches"""
    def __init__(self, search_name, search_obj, query_db, record_db, result_db, search_db,
            mode='new', fwd_search=None, threaded=False, gui=None, no_win=True, owidget=None):
        self.sobj = search_obj
        self.qdb = query_db
        self.rdb = record_db
        self.udb = result_db
        self.sdb = search_db
        self.sdb[search_name] = search_obj
        self.mode = mode
        self.fobj = fwd_search
        self.threaded = threaded # threaded or not
        self.search_list = [] # for threading searches
        self.gui = gui # used to close
        self.no_win = no_win # whether or not to close
        self.owidget = owidget # signal back to other widget

    def get_unique_outpath(self, query, db, sep='-'):
        """Returns an outpath for a given query and database"""
        out_string = sep.join([query, db, 'out.txt'])
        if self.sobj.output_location: # not None
            return os.path.join(self.sobj.output_location, out_string)
        else:
            return os.path.join(tmp_dir, out_string)

    def get_result_id(self, search_name, query, db, sep='-'):
        """Returns a unique name for each result object"""
        return sep.join([search_name, query, db])

    def run(self):
        """Runs the search using information in the search object and databases"""
        for qid in self.sobj.queries: # list of qids
            if self.mode == 'new': # new search from user input
                qobj = self.qdb[qid] # fetch associated object from db
            elif self.mode == 'old': # search from previous search
                # This loop is kind of gross... maybe don't nest objects within search results?
                # Alternatively, find a more direct way of getting query without so much looping?
                qsobj = self.qdb.fetch_search(self.fobj.name)
                for uid in qsobj.list_entries():
                    #print(uid)
                    uobj = qsobj.fetch_entry(uid)
                    for query in uobj.list_entries():
                        #print(query)
                        if query == qid:
                            qobj = uobj.fetch_entry(query)
            if qobj.target_db: # i.e. is not None
                if not qobj.target_db in self.sobj.databases: # don't add duplicates
                    self.sobj.databases.append(qobj.target_db) # keep track of databases
                self.call_run(self.sobj.name, qid, qobj, qobj.target_db)
            else: # run for all dbs
                for db in self.sobj.databases:
                    self.call_run(self.sobj.name, qid, qobj, db)
        if self.threaded:
            if not self.gui:
                print('calling popup')
                popup = Tk()
            else:
                popup = self.gui
            ts = threaded_search.ProgressFrame(self.sobj.algorithm, self.search_list,
                    callback = self.threaded_callback, parent=popup, no_win=self.no_win)
            ts.run()
            # store the thread on a global for program awareness
            configs['threads'].add_thread()
        else:
            # now ensure dbs are updated
            configs['search_db'].commit()
            configs['result_db'].commit()

    def call_run(self, sid, qid, qobj, db):
        """Calls the run_one for each query/db pair"""
        uniq_out = self.get_unique_outpath(qid, db)
        result_id = self.get_result_id(sid, qid, db)
        db_obj = self.rdb[db]
        for v in db_obj.files.values():
            if v.filetype == self.sobj.db_type:
                dbf = v.filepath # worry about more than one possible file?
        if self.threaded:
            self.search_list.append([self.sobj,qid, db, qobj, dbf, uniq_out, self.udb, result_id])
        else:
            self.run_one(qid, db, qobj, dbf, uniq_out, self.udb, result_id)

    def run_one(self, qid, db, qobj, dbf, outpath, result_db, result_id):
        """Runs each individual search"""
        if self.sobj.algorithm == 'blast':
            if self.sobj.q_type == 'protein' and self.sobj.db_type == 'protein':
                blast_search = blast_setup.BLASTp(blast_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            blast_search.run_from_stdin()
        elif self.sobj.algorithm == 'hmmer':
            if self.sobj.q_type == 'protein' and self.sobj.db_type == 'protein':
                hmmer_search = hmmer_setup.ProtHMMer(hmmer_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            hmmer_search.run_from_stdin()
        robj = result_obj.Result(result_id, self.sobj.algorithm,
                self.sobj.q_type, self.sobj.db_type, qid, db, self.sobj.name,
                outpath)
        #print("Adding {} result to {} search object".format(result_id,self.sobj))
        self.sobj.add_result(result_id) # function ensures persistent object updated
        #print("Adding {} rid and {} robj to result db".format(result_id,robj))
        self.udb[result_id] = robj # add to result db

    def parse(self):
        """Parses output files from search"""
        for result in self.sobj.results:
            robj = self.udb[result]
            # Parse result first
            if robj.algorithm == 'blast':
                blast_result = NCBIXML.read(open(robj.outpath))
                robj.parsed_result = blast_result
            elif robj.algorithm == 'hmmer':
                # need to sort out prot/nuc later
                hmmer_result = hmmer_parser.HMMsearchParser(robj.outpath).parse()
                robj.parsed_result = hmmer_result
            # Set parsed flag and check for object removal
            robj.parsed = True
            if not self.sobj.keep_output: #and robj.parsed:
                os.remove(robj.outpath)
            self.udb[result] = robj # add back to db

    def threaded_callback(self, *robjs):
        """Takes care of doing things with the completed searches"""
        #print("Calling thread callback function")
        # remove thread from global first
        configs['threads'].remove_thread()
        try:
            for robj in robjs:
                rid = robj.name
                self.sobj.add_result(rid)
                self.udb[rid] = robj
            print('parsing output')
            self.parse()
        finally: # commit no matter what?
            # now ensure dbs are updated
            configs['search_db'].commit()
            configs['result_db'].commit()
            # signal to finish searches
            if self.owidget:
                self.owidget._cont()

