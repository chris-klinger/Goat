"""
New module for dealing with search objects. These are now objects stored under a
node in the main ZODB database, rather than separate files.
"""

from persistent import Persistent

class Search(Persistent):
    """Generic Search class"""
    def __init__(self, name, algorithm, q_type, db_type, queries, databases,
            keep_output=False, output_location=None, **params):
        self.name = name
        self.algorithm = algorithm
        self.q_type = q_type # e.g. protein
        self.db_type = db_type # e.g. protein
        self.queries = queries # list of qids
        self.databases = databases # list of db files, or records?
        self.keep_output = keep_output
        self.output_location = output_location # None if no location is specified
        self.results = [] # pointer to eventual results
        self.params = params # possibly empty dictionary of additional program params
