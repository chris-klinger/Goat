"""
This module contains helper functions/classes for dealing with intermediate search
results, including creating new or reverse searches from them.
"""

from Bio import SeqIO

from searches import search_util
from queries import query_obj

class IntermediateQuery:
    def __init__(self, result_obj, query_db, record_db, mode='reverse'):
        self.uobj = result_obj
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
        """Add each new query object to the result_obj"""
        if self.smode == 'reverse':
            qobj = self.qdb[self.uobj.query]
            tdb = qobj.record # target defined if reverse search
        else:
            tdb = None
        for record in self.get_titles():
            self.uobj.add_query(query_obj.Query(record.id, record.name,
                record.description, sequence=record.seq, record=self.uobj.database,
                target_db=tdb, original_query=self.uobj.query))
