"""
This module contains code to actually perform searches in Goat. Idea is to take a
search object, and pointers to the query, record, and results databases. Using the
information in the search object, each query/database search is ran and used to
generate a new results object in the results db. Each result object is also added
to the search object in order to keep track of which results belong to which
search.
"""

import os

from Bio.Blast import NCBIXML

from searches.blast import blast_setup
from results import result_obj

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class SearchRunner:
    """Actually runs searches"""
    def __init__(self, search_obj, query_db, record_db, result_db,
            mode='new', fwd_search=None):
        self.sobj = search_obj
        self.qdb = query_db
        self.rdb = record_db
        self.udb = result_db
        self.mode = mode
        self.fobj = fwd_search

    def get_unique_outpath(self, query, db, sep='-'):
        """Returns an outpath for a given query and database"""
        out_string = sep.join([query, db, 'out.txt'])
        if self.sobj.output_location: # not None
            return os.path.join(self.sobj.output_location, out_string)
        else:
            return os.path.join(tmp_dir, out_string)

    def get_result_id(self, query, db, sep='-'):
        """Returns a unique name for each result object"""
        return sep.join([query, db])

    def run(self):
        """Runs the search using information in the search object and databases"""
        for qid in self.sobj.queries: # list of qids
            if self.mode == 'new': # new search from user input
                qobj = self.qdb[qid] # fetch associated object from db
            elif self.mode == 'old': # search from previous search
                # This loop is kind of gross... maybe don't nest objects within search results?
                qsobj = self.qdb.fetch_search(self.fobj.name)
                for uid in qsobj.list_entries():
                    print(uid)
                    uobj = qsobj.fetch_entry(uid)
                    for query in uobj.list_entries():
                        print(query)
                        if query == qid:
                            qobj = uobj.fetch_entry(query)
            if qobj.target_db: # i.e. is not None
                self.call_run(qid, qobj, qobj.target_db)
            else: # run for all dbs
                for db in self.sobj.databases:
                    self.call_run(qid, qobj, db)

    def call_run(self, qid, qobj, db):
        """Calls the run_one for each query/db pair"""
        uniq_out = self.get_unique_outpath(qid, db)
        result_id = self.get_result_id(qid, db)
        db_obj = self.rdb[db]
        for v in db_obj.files.values():
            if v.filetype == self.sobj.db_type:
                dbf = v.filepath # worry about more than one possible file?
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
            robj = result_obj.Result(result_id, self.sobj.algorithm,
                self.sobj.q_type, self.sobj.db_type, qid, db, self.sobj.name,
                outpath)
            print("Adding {} result to {} search object".format(result_id,self.sobj))
            self.sobj.add_result(result_id) # function ensures persistent object updated
            print("Adding {} rid and {} robj to result db".format(result_id,robj))
            self.udb[result_id] = robj # add to result db
        elif self.sobj.algorithm == 'hmmer':
            pass # include more algorithms later

    def parse(self):
        """Parses output files from search"""
        for result in self.sobj.results:
            robj = self.udb[result]
            if robj.algorithm == 'blast':
                blast_result = NCBIXML.read(open(robj.outpath))
                robj.parsed_result = blast_result
                robj.parsed = True
            if not self.sobj.keep_output and robj.parsed:
                os.remove(robj.outpath)
            self.udb[result] = robj # add back to db
