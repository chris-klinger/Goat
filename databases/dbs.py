"""
This module contains condensed code for implementing individual DB layers to the
underlying ZODB database in Goat. A generic Superclass provides basic access and
methods, and then these can be further elaborated in subclasses.
"""

#from BTrees.OOBTree import OOBTree

from bin.initialize_goat import configs

#from queries import query_set

class DB:
    """
    Generic superclass for all specific dbs to subclass. Assumes the underlying
    GoatDB object has established the connection, and simply ties into a node on
    this database to route calls through.
    """
    def __init__(self, node=None):
        self.db = configs['goat_db']
        self.node = node

    def commit(self):
        """Commits all marked changes in the main db"""
        self.db._commit()

    def close(self):
        """Closes the main db"""
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

    def is_empty(self):
        """Convenicence function"""
        length = sum(1 for _ in self.list_entries())  # Length of a generator
        return length == 0

class QueryDB(DB):
    def __init__(self):
        DB.__init__(self, 'query_db')

class MiscQDB(DB):
    def __init__(self):
        DB.__init__(self, 'misc_queries')

class SearchQDB(DB):
    def __init__(self):
        DB.__init__(self, 'search_queries')

class QSetDB(DB):
    def __init__(self):
        DB.__init__(self, 'query_sets')

    def remove_from_all(self, qid):
        """
        Called from main_query_gui on query removal; checks all 'qids' attrs of
        all sets in database and removes the qid from all.
        """
        for qset in self.list_entries():
            print(qset)
            try:
                set_obj = self.__getitem__(qset)
                print(set_obj)
                set_obj.entries.remove(qid)
            except ValueError: # not in list
                pass

class RecordDB(DB):
    def __init__(self):
        DB.__init__(self, 'record_db')

class RSetDB(DB):
    def __init__(self):
        DB.__init__(self, 'record_sets')

class ResultDB(DB):
    def __init__(self):
        DB.__init__(self, 'result_db')

class SearchDB(DB):
    def __init__(self):
        DB.__init__(self, 'search_db')

class SettingsDB(DB):
    def __init__(self):
        DB.__init__(self, 'settings_db')

class SSetDB(DB):
    def __init__(self):
        DB.__init__(self, 'settings_sets')

class SummaryDB(DB):
    def __init__(self):
        DB.__init__(self, 'summary_db')
