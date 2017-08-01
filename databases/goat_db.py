"""
This module contains code for a top-level interface for the ZODB-style database
storing most of the information required for Goat. Each group of data within
the database is encapsulated by a separate class, each with a reference to the
corresponding root attribute. Further classes incorporate the objects themselves
and the code necessary to perform manipulations on them.
"""

import os
from threading import Lock

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
        else: # first time accessing
            self.storage = FileStorage.FileStorage(filepath)
            db = DB(self.storage)
            connection = db.open()
            self.root = connection.root()
            # create data structures
            self.root['queries'] = OOBTree()
            self.root['records'] = OOBTree()
            self.root['results'] = OOBTree()
            self.root['searches'] = OOBTree()
            self.root['summaries'] = OOBTree()
        self._lock = Lock()

    def _commit(self):
        import transaction
        with self._lock:
            transaction.commit()

    def close(self):
        self.storage.close()

    def list_entries(self, node):
        with self._lock:
            return self.root[node].keys() # note: iterator!

    def fetch_entry(self, node, key):
        with self._lock:
            return self.root[node][key]

    def put_entry(self, node, key, entry):
        with self._lock:
            self.root[node][key] = entry

    def remove_entry(self, node, key):
        with self._lock:
            del self.root[node][key]

