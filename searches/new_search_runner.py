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

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'
hmmer_path = '/Users/cklinger/src/hmmer-3.1b1-macosx-intel/src'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class SearchRunner:
    """Actually runs searches"""
    def __init__(self, sobj, mode='new', other_widget=None):
        # dbs are global
        self.qdb = configs['query_db']
        self.mqdb = configs['misc_queries']
        self.sqdb = configs['search_queries']
        self.rdb = configs['record_db']
        self.udb = configs['result_db']
        self.sdb = configs['search_db']
        # arguments fed in to object
        self.sobj = sobj
        self.mode = mode
        self.other = other_widget # signal back to other widget

    def get_unique_outpath(self, query, db, sep='-'):
        """Returns an outpath for a given query and database"""
        query = query.replace('/','-') # '/' is linux separator, confuses file read/write operations
        out_string = sep.join([query, db, 'out.txt'])
        if self.sobj.output_location: # not None
            #print(self.sobj.output_location)
            return os.path.join(self.sobj.output_location, out_string)
        else:
            #print('using default location')
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
            elif self.mode == 'rev': # search from previous search
                qobj = self.sqdb[qid] # fetch from other query db
            elif self.mode == 'racc': # search for raccs
                try:
                    qobj = self.qdb[qid] # qobj should already be in the query db
                except KeyError: # not in regular qdb
                    qobj = self.mqdb[qid]
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
        if os.path.exists(uniq_out):
            self.add_result(result_id, qid, qobj, db, uniq_out)
        else: # actually run the search
            db_obj = self.rdb[db]
            for v in db_obj.files.values():
                if db_type: # specified by query, not search_obj
                    if v.filetype == db_type:
                        dbf = v.filepath
                elif v.filetype == self.sobj.db_type:
                    dbf = v.filepath # worry about more than one possible file?
                    db_type = self.sobj.db_type
            self.run_one(qid, db, qobj, dbf, db_type, uniq_out, self.udb, result_id)

    def run_one(self, qid, db, qobj, dbf, db_type, outpath, result_db, result_id):
        """Runs each individual search"""
        # query type can be specified on individual queries or globally on sobj
        q_type = qobj.alphabet if qobj.alphabet else self.sobj.q_type
        if self.sobj.algorithm == 'blast':
            if q_type == 'protein' and db_type == 'protein':
                blast_search = blast_setup.BLASTp(blast_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            blast_search.run_from_stdin()
        elif self.sobj.algorithm == 'hmmer':
            if q_type == 'protein' and db_type == 'protein':
                hmmer_search = hmmer_setup.ProtHMMer(hmmer_path, qobj,
                        dbf, outpath)
            else:
                pass # sort out eventually
            hmmer_search.run_from_stdin()
        self.add_result(result_id, qid, qobj, db, outpath)
        #robj = result_obj.Result(result_id, self.sobj.algorithm,
        #        self.sobj.q_type, self.sobj.db_type, qid, db, self.sobj.name,
        #        outpath)
        # Add specified query/record info, if available
        #try:
        #    if qobj.spec_qid:
        #        robj.spec_qid = qobj.spec_qid
        #    if qobj.spec_record:
        #        robj.spec_record = qobj.spec_record
        #except(AttributeError):
        #    pass # not applicable
        # Add result object to search object and result database
        #self.sobj.add_result(result_id) # function ensures persistent object updated
        #self.udb[result_id] = robj # add to result db

    def add_result(self, result_id, qid, qobj, db, outpath):
        """Separates running search from adding info"""
        robj = result_obj.Result(result_id, self.sobj.algorithm,
                self.sobj.q_type, self.sobj.db_type, qid, db,
                self.sobj.name, outpath)
        # Add specified query/record info, if available
        try:
            if qobj.spec_qid:
                robj.spec_qid = qobj.spec_qid
            if qobj.spec_record:
                robj.spec_record = qobj.spec_record
        except(AttributeError):
            pass # not applicable
        # Add result object to search object and result database
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
            #print("adding result object for BLAST")
            try:
                blast_result = NCBIXML.read(open(robj.outpath))
                robj.parsed_result = blast_result
            except:
                print("Could not parse file {}".format(robj.outpath))
        elif robj.algorithm == 'hmmer':
            # need to sort out prot/nuc later
            hmmer_result = hmmer_parser.HMMsearchParser(robj.outpath).parse()
            robj.parsed_result = hmmer_result
        # Set parsed flag and check for object removal
        robj.parsed = True
        if not self.sobj.keep_output: #and robj.parsed:
            #print("removing output")
            self.other.add_file_to_delete(robj.outpath)
            #os.remove(robj.outpath)

