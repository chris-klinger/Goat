"""
Module for implementing sets of queries, i.e. those that come from a single
file? Should this be different than groups eventually?

At minimum, needs to hold a collection of queries.
"""

from persistent import Persistent

class QuerySet(Persistent):
    """Persistent object that holds references to queries within the actual
    QueryDB. Idea is to make display of queries easier as the number of
    possible queries grows much larger.
    """
    def __init__(self):
        self.qdict = {}
        try:
            self._all = self.qdict['_ALL']
        except:
            self.qdict['_ALL'] = []
            self._all = self.qdict['_ALL']


    def list_query_sets(self):
        """Convenience function"""
        for entry in self.qdict.keys():
            if entry != '_ALL':
                yield entry
        #return list(self.qdict.keys())

    def add_query_set(self, set_name, *qids):
        """Adds a set along with any associated queries"""
        self.qdict[set_name] = [] # initialize to an empty list
        if len(qids) > 0:
            for qid in qids:
                self.add_query(set_name, qid)
        self._p_changed = 1

    def remove_query_set(self, set_name):
        """Remove a set and all pointers"""
        if not set_name == '_ALL': # do not allow deletion
            del self.qdict[set_name]
            self._p_changed = 1

    def add_query(self, set_name, qid):
        """Adds a query to the specified set"""
        self.qdict[set_name].append(qid)
        self._p_changed = 1

    def remove_query(self, set_name, qid):
        """Removes a query from the specified set"""
        slist = self.qdict[set_name]
        slist.remove(qid)
        self._p_changed = 1
