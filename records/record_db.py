"""
This module contains code for dealing with record objects in the ZODB-style
backend database.
"""

# will be changed to records eventually
from databases import record_obj

class RecordDB:
    def __init__(self, db_obj):
        self.db = db_obj
        self.node = 'records'

    def commit(self):
        self.db._commit()

    def close(self):
        self.db._close()

    def __getitem__(self, key):
        """Delegates to connection"""
        #print(key)
        return self.db.fetch_entry(self.node, key)

    def __setitem__(self, key, value):
        """Delegates to connection"""
        self.db.put_entry(self.node, key, value)

    def list_records(self):
        """Convenience function"""
        for entry in self.db.list_entries(self.node):
            #print(entry)
            if entry != '_Groups':
                yield entry

    def add_record(self, record_identity, **kwargs):
        """Creates and populates a new Record"""
        new_record = record_obj.Record(record_identity)
        self.db.put_entry(self.node, record_identity, new_record)
        self.update_record(record_identity, **kwargs)

    def remove_record(self, record_identity):
        """Removes a Record"""
        self.db.remove_entry(self.node, record_identity)

    def update_record(self, record_identity, **kwargs):
        """Updates a pre-existing Record with key,value pairs"""
        record_obj = self.db.fetch_entry(self.node, record_identity)
        for attr,value in kwargs.items():
            setattr(record_obj, attr, value)

    def add_record_file(self, record_identity, filename, filepath, filetype, **kwargs):
        """Delegates to Record object"""
        record_obj = self.db.fetch_entry(self.node, record_identity)
        record_obj.add_file(filename, filepath, filetype, **kwargs)

    def remove_record_file(self, record_identity, filename):
        """Delegates to Record object"""
        record_obj = self.db.fetch_entry(self.node, record_identity)
        record_obj.remove_file(filename)

    def update_record_file(self, record_identity, filename, **kwargs):
        """Delegates to Record object"""
        record_obj = self.db.fetch_entry(self.node, record_identity)
        record_obj.update_file(filename, **kwargs)
