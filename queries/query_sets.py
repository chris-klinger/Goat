"""
Module with code for the updated implementation of query sets. In this view, sets
are just objects in the database, each one with a different tag depending on the
kind of queries that are present within them.
"""

from persistent import Persistent

class QuerySet(Persistent):
    def __init__(self, name, query_type):
        self.name = name
        self.qtype = query_type
        self.qids = []

    def add_qids(self, query_list):
        """Ensures persistence"""
        self.qids = query_list
        self._p_changed = 1

    def list_queries(self):
        """Convenience function"""
        return self.qids
