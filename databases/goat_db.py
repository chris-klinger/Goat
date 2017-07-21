"""
This module contains code for a top-level interface for the ZODB-style database
storing most of the information required for Goat. Each group of data within
the database is encapsulated by a separate class, each with a reference to the
corresponding root attribute. Further classes incorporate the objects themselves
and the code necessary to perform manipulations on them.
"""

import os

from ZODB import FileStorage, DB
from BTrees.OOBTree import OOBTree

class GoatDB:
    """
    Handles connecting to the underlying ZODB database, commiting data
    in transactions, and closing the connection.
    """
    def __init__(self, filepath):
        """Connects to database file on instantiation"""
        if os.path.exists(filepath):
            self.storage = FileStorage.FileStorage(filepath)
            db = DB(self.storage)
            connection = db.open()
            self.root = connection.root()
            if not 'searches' in self.root.keys():
                self.root['searches'] = OOBTree()
        else: # first time accessing
            self.storage = FileStorage.FileStorage(filepath)
            db = DB(self.storage)
            connection = db.open()
            self.root = connection.root()
            # create data structures
            self.root['records'] = OOBTree()
            self.root['queries'] = OOBTree()
            self.root['searches'] = OOBTree()
            self.root['results'] = OOBTree()
            self.root['summaries'] = OOBTree()

    def _commit(self):
        import transaction
        transaction.commit()

    def _close(self):
        #self._commit() # one final commit to be sure
        self.storage.close()

    def list_entries(self, node):
        return self.root[node].keys() # note: iterator!

    def fetch_entry(self, node, key):
        #print(node)
        #print(key)
        return self.root[node][key]

    def put_entry(self, node, key, entry):
        self.root[node][key] = entry

    def remove_entry(self, node, key):
        del self.root[node][key]

