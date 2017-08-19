"""
New module for dealing with search objects. These are now objects stored under a
node in the main ZODB database, rather than separate files.
"""

from persistent import Persistent

class Search(Persistent):
    """Generic Search class"""
    def __init__(self, name, algorithm, q_type, db_type, queries, databases,
            keep_output=False, output_location=None, rev_record=None, **params):
        self.name = name
        self.algorithm = algorithm # note, lowercase!
        self.q_type = q_type # e.g. protein
        self.db_type = db_type # e.g. protein
        self.queries = queries # list of qids
        self.databases = databases # list of db files, or records?
        self.keep_output = keep_output
        self.output_location = output_location # None if no location is specified
        self.params = params # possibly empty dictionary of additional program params
        self.rev_record = rev_record # for reverse searches using fwd HMM/MSA
        self.results = [] # pointer to eventual results

    def list_results(self):
        """Convenience function"""
        return list(self.results)

    def add_result(self, rid):
        """Adds rid to internal list; ensures object is marked for update"""
        self.results.append(rid)
        self._p_changed = 1
