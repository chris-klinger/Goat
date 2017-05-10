"""
This module contains code to implement a new ZODB impementation of search
databases. In this realization, each search corresponds to a separate
filestorage object, each with its own set of query, result, and summary
objects, supported under a single root as single persistent data structures
to which other objects, each inheriting from persistent in turn, can be
added. For now, will also add searches to this same file dump.
"""

from ZODB import FileStorage, DB
from BTrees.OOBTree import OOBTree

#from searches import search_setup

class SearchDB:
    """
    Encapsulates the underlying ZODB database. Each search database has
    attributes to store information on queries, databases used, results
    and summaries produced, and an actual record of the search performed,
    including all relevant parameters.
    """
    def __init__(self, filepath):
        """Connects to database file on instantiation"""
        self.storage = FileStorage.FileStorage(filepath)
        db = DB(self.storage)
        connection = db.open()
        self.root = connection.root()
        self.searches = OOBTree() # tree for one value? Maintain data structure?
        self.root['searches'] = self.searches
        self.queries = OOBTree() # make a persistent data structure
        self.root['queries'] = self.queries # map it to root
        self.dbs = OOBTree()
        self.root['dbs'] = self.dbs
        self.results = OOBTree()
        self.root['results'] = self.results
        self.summaries = OOBTree()
        self.root['summaries'] = self.summaries

    def __getitem__(self, keypair):
        rtype,key = keypair
        return self.root[rtype][key] # call with tuple containing desired subdir?

    def __setitem__(self, keypair, value):
        rtype,key = keypair
        self.root[rtype][key] = value

    def commit(self):
        import transaction
        transaction.commit()

    def close(self):
        self.commit()
        self.storage.close()

    def list_entries(self, rtype):
        return self.root[rtype].keys() # note: iterator!

    def add_entry(self, rtype, key, entry):
        self.root[rtype][key] = entry

    def remove_entry(self, rtype, key):
        del self.root[rtype][key]
