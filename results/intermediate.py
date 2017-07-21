"""
This module contains helper functions/classes for dealing with intermediate search
results, including creating new or reverse searches from them.
"""

from Bio import SeqIO

from searches import search_util
from queries import query_obj, search_query

class Search2Queries:
    def __init__(self, search_obj, result_db, query_db, record_db, mode='reverse'):
        self.sobj = search_obj
        self.udb = result_db
        self.qdb = query_db
        self.rdb = record_db
        self.mode = mode

    def get_result_objs(self):
        """Goes through and fetches the robj for each rid"""
        for rid in self.sobj.list_results():
            robj = self.udb[rid]
            yield robj

    def populate_search_queries(self):
        """Populates queries for each result"""
        search_result = search_query.SearchResult()
        for robj in self.get_result_objs:
            r2q = Result2Queries(robj, self.qdb, self.rdb, self.mode)
            rqobj = r2q.get_queries() # returns a sub-object populated with queries for each result
            search_result.add_entry(robj.name, rqobj)
        self.qdb.add_search(self.sobj.name, search_result)

class Result2Queries:
    def __init__(self, result_obj, query_db, record_db, mode='reverse'):
        self.robj = result_obj
        self.qdb = query_db
        self.rdb = record_db
        self.smode = mode

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

    def get_queries(self):
        """Adds new query objects; these are present both as a list of qids in
        the result_obj and as query objects in the search node of the QueryDB"""
        result = search_query.SearchResult() # same object for searches and search results
        if self.smode == 'reverse':
            qobj = self.qdb[self.uobj.query]
            tdb = qobj.record # target defined if reverse search
        else:
            tdb = None
        for record in self.get_titles():
            qobj = query_obj.Query(record.id, record.name,
                record.description, sequence=record.seq, record=self.uobj.database,
                target_db=tdb, original_query=self.uobj.query)
            self.robj.add_query(record.id)
            result.add_entry(record.id, qobj)
        return result
