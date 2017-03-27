"""
This module contains code for new ZODB implementation of databases. The basic idea
here is to encapsulate the basic operation of the database, as before, and to add
functionality to add/remove/change various attributes.

One question that needs to be considered is how best to deal with the atomic nature
of database transactions. Ideally, would attempt to make all updates per user request
and then only commit once this is complete. This then requires careful consideration
of the interaction model through the GUI?
"""

from ZODB import FileStorage, DB

from databases import record_obj

class RecordDB:
    """
    Generic object encapsulating the underlying ZODB database structure. Contains
    logic to manage modifying underlying record objects in an atomic manner
    regardless of number of changes per transaction. Also handles connection logic
    in init function.
    """
    def __init__(self, filepath):
        """Connects to database file on instantiation"""
        self.storage = FileStorage.FileStorage(filepath)
        db = DB(self.storage)
        connection = db.open()
        self.root = connection.root() # Dict-like object for storing records

    def __getitem__(self, key):
        return self.root[key] # Routes index to root node

    def __setitem__(self, key, value):
        self.root[key] = value # Routes assignment to root node

    def __getattr__(self, attr):
        return getattr(self.root, attr) # Might be useful in case of direct lookup?

    def commit(self):
        """Convenience function"""
        import transaction
        transaction.commit()

    def close(self):
        """Ensures unsaved changes are commited and closes file connection"""
        self.commit() # Final commit to be sure
        self.storage.close()

    def list_records(self):
        """Convenience function"""
        return self.root.keys()

    def add_record(self, record_identity, **kwargs):
        """Creates and populates a new Record"""
        try:
            new_record = record_obj.Record(record_identity)
            self.root[record_identity] = new_record
            self.update_record(record_identity, **kwargs)
            self.commit() # change only commits if everything went well
        except: # What would throw an error?
            pass # Should raise again to let toplevel know

    def remove_record(self, record_identity):
        """Removes a Record"""
        try:
            del self.root[record_identity]
            self.commit()
        except:
            pass

    def update_record(self, record_identity, **kwargs):
        """Updates a pre-existing Record with key,value pairs"""
        try:
            record_obj = self.root[record_identity]
            for attr,value in kwargs:
                setattr(record_obj, attr, value)
            self.commit()
        except:
            pass

    def add_record_file(self, record_identity, filename, filepath, **kwargs):
        """Delegates to Record object"""
        try:
            record_obj = self.root[record_identity]
            record_obj.add_file(filename, filepath, **kwargs)
            self.commit()
        except:
            pass

    def remove_record_file(self, record_identity, filename):
        """Delegates to Record object"""
        try:
            record_obj = self.root[record_identity]
            record_obj.remove_file(filename)
            self.commit()
        except:
            pass

    def update_record_file(self, record_identity, filename, **kwargs):
        """Delegates to Record object"""
        try:
            record_obj = self.root[record_identity]
            record_obj.update_file(filename, **kwargs)
            self.commit()
        except:
            pass
