"""
This module contains code to run searches from search objects in Goat. Idea is
that this code should not care about whether or not the search is threaded, and
simply run each search in sequential order.
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
    def __init__(self, sobj, mode='new', other_widget=None):
        # dbs are global
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']
        self.udb = configs['result_db']
        self.sdb = configs['search_db']
        # arguments fed in to object
        self.sobj = sobj
        self.mode = mode
        self.other = other_widget # signal back to other widget

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
            # First half of code determines how to get qobj
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
            elif self.mode == 'racc': # search for raccs
                qobj = self.qdb[qid] # qobj should already be in the query db
            # Second half of code determines how to call the run
            if qobj.target_db: # i.e. is not None
                if not qobj.target_db in self.sobj.databases: # don't add duplicates
                    self.sobj.databases.append(qobj.target_db) # keep track of databases
                self.call_run(self.sobj.name, qid, qobj, qobj.target_db)
            elif self.mode == 'racc':
                target_db = qobj.record # search against self
                self.call_run(self.sobj.name, qid, qobj, target_db, db_type=qobj.alphabet)
            else: # run for all dbs
                for db in self.sobj.databases:
                    self.call_run(self.sobj.name, qid, qobj, db)
            if self.other:
                self.other.increment_search_count()

    def call_run(self, sid, qid, qobj, db, db_type=None):
        """Calls the run_one for each query/db pair"""
        uniq_out = self.get_unique_outpath(qid, db)
        result_id = self.get_result_id(sid, qid, db)
        db_obj = self.rdb[db]
        for v in db_obj.files.values():
            if db_type: # specified by query, not search_obj
                if v.filetype == db_type:
                    dbf = v.filepath
            elif v.filetype == self.sobj.db_type:
                dbf = v.filepath # worry about more than one possible file?
                db_type == self.sobj.db_type
            self.run_one(qid, db, qobj, dbf, db_type, uniq_out, self.udb, result_id)

    def run_one(self, qid, db, qobj, dbf, db_type, outpath, result_db, result_id):
        """Runs each individual search"""
        if self.sobj.algorithm == 'blast':
            if qobj.alphabet == 'protein' and db_type == 'protein':
                blast_search = blast_setup.BLASTp(blast_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            blast_search.run_from_stdin()
        elif self.sobj.algorithm == 'hmmer':
            if qobj.alphabet == 'protein' and db_type == 'protein':
                hmmer_search = hmmer_setup.ProtHMMer(hmmer_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            hmmer_search.run_from_stdin()
        robj = result_obj.Result(result_id, self.sobj.algorithm,
                self.sobj.q_type, self.sobj.db_type, qid, db, self.sobj.name,
                outpath)
        self.sobj.add_result(result_id) # function ensures persistent object updated
        self.udb[result_id] = robj # add to result db

    def parse(self):
        """Parses output files from search"""
        for result in self.sobj.results:
            robj = self.udb[result]
            self.parse_one(robj)

    def parse_one(self, robj):
        """Parse an individual result object result"""
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

    def threaded_callback(self, *robjs):
        """Takes care of doing things with the completed searches"""
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

    def racc_callback(self, sobj, *robjs):
        """Parses output files, adds accs to qobjs, and then removes all db entries"""
        configs['threads'].remove_thread()
        try:
            for robj in robjs:
                qid = robj.query # actually qid
                qobj = self.qdb[qid]
                self.parse_one(robj)
                self.add_raccs(qobj, robj.parsed_result)
        finally:
            # don't want to keep these in the db
            for rid in self.sobj.results:
                self.udb.remove_entry(rid)
            self.sdb.remove_entry(self.sobj.name)

    def add_self_blast(self, qobj, blast_result):
        """Adds hits to qobj attribute before removal"""
        lines = []
        seen = set()
        for hit in blast_result.descriptions:
            new_title = search_util.remove_blast_header(hit.title)
            if not new_title in seen:
                lines.append([new_title, hit.e])
                seen.add(new_title)
        self.all_accs = lines
