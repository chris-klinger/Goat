"""
Module description
"""

from searches import search_query
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
            if entry != '_Sets':
                yield entry

    def add_query(self, query_identity, **kwargs):
        """Creates and populates a new Record"""
        new_query = search_query.Query(query_identity)
        self.db.put_entry(self.node, query_identity, new_query)
        self.update_record(query_identity, **kwargs)

    def remove_query(self, query_identity):
        """Removes a Record"""
        self.db.remove_entry(self.node, query_identity)

    def update_query(self, query_identity, **kwargs):
        """Updates a pre-existing Record with key,value pairs"""
        query_obj = self.db.fetch_entry(self.node, query_identity)
        for attr,value in kwargs.items():
            setattr(query_obj, attr, value)


