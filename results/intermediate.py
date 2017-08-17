"""
This module contains helper functions/classes for dealing with intermediate search
results, including creating new or reverse searches from them.
"""

from Bio import SeqIO

from bin.initialize_goat import configs

from searches import search_util
from queries import query_objects

class Search2Queries:
    def __init__(self, search_obj, mode='reverse'):
        self.sobj = search_obj
        self.mode = mode
        # get dbs from global variables
        self.sqdb = configs['search_queries']
        self.udb = configs['result_db']
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']

    def get_result_objs(self):
        """Goes through and fetches the robj for each rid"""
        for rid in self.sobj.list_results():
            robj = self.udb[rid]
            yield robj

    def populate_search_queries(self):
        """Populates queries for each result"""
        for robj in self.get_result_objs():
            r2q = Result2Queries(robj, self.mode)
            r2q.add_queries() # adds queries to search queries db

class Result2Queries:
    def __init__(self, result_obj, mode='reverse'):
        self.uobj = result_obj
        self.smode = mode
        # dbs are global
        self.qdb = configs['query_db']
        self.rdb = configs['record_db']
        self.sqdb = configs['search_queries']

    def get_titles(self):
        """Return a list of hit names"""
        desired_seqs = []
        seq_records = []
        desired_seqs.extend([search_util.remove_blast_header(hit.title)
            for hit in self.uobj.parsed_result.descriptions])
        for record in SeqIO.parse(self.get_record_file(), "fasta"):
            if record.description in desired_seqs:
                seq_records.append(record)
        return seq_records

    def get_record_file(self):
        """Return the full handle to the db record file"""
        robj = self.rdb[self.uobj.database] # fetch record object
        for v in robj.files.values(): # should maybe encapsulate better
            if v.filetype == self.uobj.db_type:
                return v.filepath

    def add_queries(self):
        """
        Adds new query objects; these are present both as a list of qids in
        the result_obj and as query objects in the search_queries DB
        """
        if self.smode == 'reverse':
            qobj = self.qdb[self.uobj.query]
            tdb = qobj.record # target defined if reverse search
        else:
            tdb = None
        for record in self.get_titles():
            qobj = query_objects.SeqQuery(
                    identity=record.id,
                    name=record.name,
                    description=record.description,
                    sequence=record.seq,
                    record=self.uobj.database,
                    target_db=tdb,
                    original_query=self.uobj.query)
            self.uobj.add_int_query(record.id)
            self.sqdb.add_entry(record.id, qobj) # adds the qobj to the int database
