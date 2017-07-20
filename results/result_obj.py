"""
New module for dealing with result objects.
"""

from persistent import Persistent

class Result(Persistent):
    """Generic Result class"""
    def __init__(self, name, algorithm, q_type, db_type, query, database,
            search_name, outpath=None, original_query=None):
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
