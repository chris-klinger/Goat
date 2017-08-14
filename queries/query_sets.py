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
        self.num_queries = 0

    def add_qids(self, query_list):
        """Ensures persistence"""
        self.qids = query_list
        self.calc_num_queries()
        self._p_changed = 1

    def list_queries(self):
        """Convenience function"""
        return self.qids

    def calc_num_queries(self):
        """Called each time query list is updated to change attribute"""
        self.num_queries = len(self.qids)


