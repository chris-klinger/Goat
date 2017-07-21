"""
This module contatins code to deal with queries resulting from searches in the query
database. These queries are kept in separate objects and are hidden from the user
for internal use.
"""

from BTrees.OOBTree import OOBTree

class SearchResult:
    def __init__(self):
        self.entries = OOBTree()

    def fetch_entry(self, oid):
        """Convenience function"""
        for entry in self.list_entries():
            if entry == oid:
                return self.entries[entry]

    def list_entries(self):
        """Convenience function"""
        for entry in self.entries.keys():
            yield entry

    def add_entry(self, oid, obj):
        """Adds a query object by ID"""
        self.entries[oid] = obj

    def remove_entry(self, oid):
        """Removes a query"""
        del self.entries[oid]
