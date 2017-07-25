"""
This module contains code for storing summary entries.

Eventually, all databases will be combined as subclasses of a generic DB
superclass, and differences will be worked out using inheritance
"""

#from searches import search_setup

class SummaryDB:
    def __init__(self, db_obj):
        """Connects to database file on instantiation"""
        self.db = db_obj
        self.node = 'summaries'

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

    def list_entries(self):
        """Convenience function"""
        for entry in self.db.list_entries(self.node):
            yield entry

    def add_entry(self, identity, obj):
        """Add or modify a search object"""
        self.db.put_entry(self.node, identity, obj)

    def remove_entry(self, identity):
        """Removes a database object"""
        self.db.remove_entry(self.node, identity)
