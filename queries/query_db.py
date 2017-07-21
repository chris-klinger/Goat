"""
Module description
"""

from BTrees.OOBTree import OOBTree

#from searches import search_query
from queries import query_set

class QueryDB:
    def __init__(self, db_obj):
        self.db = db_obj
        self.node = 'queries'
        try:
            self.sets = self.db.fetch_entry(self.node, '_Sets')
        except: # does not yet exist
            set_obj = query_set.QuerySet()
            self.db.put_entry(self.node, '_Sets', set_obj)
            self.sets = self.db.fetch_entry(self.node, '_Sets')
        try:
            self.searches = self.db.fetch_entry(self.node, '_Searches')
        except:
            search_tree = OOBTree()
            self.db.put_entry(self.node, '_Searches', search_tree)
            self.searches = self.db.fetch_entry(self.node, '_Searches')

    def commit(self):
        self.db._commit()

    def close(self):
        self.db._close()

    def __getitem__(self, key):
        """Delegates to connection"""
        return self.db.fetch_entry(self.node, key)

    def __setitem__(self, key, value):
        """Delegates to connection"""
        self.db.put_entry(self.node, key, value)

    def list_queries(self):
        """Convenience function"""
        for entry in self.db.list_entries(self.node):
            if entry != '_Sets' or '_Searches':
                yield entry

    def add_query(self, query_identity, query_obj):
        """Adds an object to the db"""
        self.db.put_entry(self.node, query_identity, query_obj)
        self.sets.add_query('_ALL',query_identity) # add to set of all queries

    def remove_query(self, query_identity):
        """Removes a Record"""
        self.db.remove_entry(self.node, query_identity)
        for qset in self.sets.list_query_sets(): # remove from all sets
            if query_identity in qset:
                self.sets.remove_query(qset, query_identity)

    # Do we want to implement methods for sets eventually as well?
    # Currently, other code directly accesses 'self.sets'

    def fetch_search(self, search_name):
        """Gets an associated search object"""
        for sname in self.searches.keys():
            if sname == search_name:
                return self.searches[sname]

    def add_search(self, search_name, search_obj):
        """Adds an object associated with a search"""
        self.searches[search_name] = search_obj

    def remove_search(self, search_name):
        """Removes a search object"""
        del self.searches[search_name]
