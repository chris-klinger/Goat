"""
New module for dealing with result objects.
"""

from persistent import Persistent

class Result(Persistent):
    """Generic Result class"""
    def __init__(self, name, algorithm, q_type, db_type, query, database,
            search_name, outpath=None, original_query=None, spec_qid=None,
            spec_record=None):
        self.name = name
        self.algorithm = algorithm
        self.q_type = q_type # e.g. protein
        self.db_type = db_type # e.g. protein
        self.query = query # qid
        self.database = database # db file/record
        self.search_name = search_name # is this needed?
        self.outpath = outpath # output file, if kept
        self.original_query = original_query # for reverse searches
        self.parsed_result = None # parsed output file object
        self.parsed = False # not parsed to begin with
        self.int_queries = [] # possibly empty; populated on first subsequent search
        # Specify qid/record for rBLAST and summary; HMMer results only
        self.spec_qid = spec_qid
        self.spec_record = spec_record

    def list_queries(self):
        """Convenience function"""
        return list(self.int_queries)

    def add_int_query(self, qid):
        """Adds qid to internal list; ensures object is marked for update"""
        self.int_queries.append(qid)
        self._p_changed = 1
