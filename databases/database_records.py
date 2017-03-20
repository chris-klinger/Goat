"""
This module contains code to work with records

Note: will need to determine how best to implement these functions together
with the underlying shelve database and record class... for now, this will
serve as a reminder of required functionality!
"""

import shelve

class Record:
    """
    A record for an organism. At minimum requires a genus and species
    value, but can also include additional information such as paths
    to associated files, timestamps, and other data pertaining to
    taxonomic affiliation, etc.
    """
    def __init__(self, genus=None, species=None):
        self.genus = genus
        self.species = species

class RecordsDB:
    """Abstracts underlying shelve database"""
    def __init__(self, db_name):
        self.db_name = db_name

    def list_records(self):
        """Utility function"""
        with shelve.open(self.db_name) as db:
            return list(db.keys())

    def check_record(self, record):
        """Checks whether a record is present"""
        for entry in self.list_records():
            if entry == record:
                return True
        return False

    def fetch_record(self, record_name):
        """Fetches a record"""
        with shelve.open(self.db_name) as db:
            return db[record_name]

    def update_record(self, record_name, record):
        """Stores back a record"""
        with shelve.open(self.db_name) as db:
            db[record_name] = record

    def add_record_obj(self, record, **kwargs):
        """Adds information to already existing records"""
        (genus,species) = record.split('_')[0], record.split('_')[1]
        with shelve.open(self.db_name) as db:
            db[record] = Record(genus, species)
        if len(kwargs) > 0:
            self.extend_record(record, **kwargs)

    def remove_record_obj(self, record):
        """Removes a record from the database"""
        with shelve.open(self.db_name) as db:
            try:
                del db[record]
            except(KeyError):
                print("Could not remove {}, no such record".format(record))

    def extend_record(self, record_name, **kwargs):
        """Adds information to pre-existing records"""
        if self.check_record(record_name):
            record = self.fetch_record(record_name)
            for attr,value in kwargs.items():
                try:
                    setattr(record, attr, value)
                except(Exception):
                    print('Error when adding value {} to record {}'.format(attr, record))
            self.update_record(record_name, record)
        else:
            print('Could not extend {}, no such record'.format(record_name))

    def reduce_record(self, record_name, *args):
        """Removes information from pre-existing records"""
        if self.check_record(record_name):
            record = self.fetch_record(record_name)
            for attr in args:
                try:
                    delattr(record, attr)
                except(Exception):
                    print('Error when removing {} from record {}'.format(attr, record))
            self.update_record(record_name, record)
        else:
            print('Could not reduce {}, no such record'.format(record_name))

    def change_record_attr(self, record_name, attr, new_value):
        """Changes one or more attributes of a record"""
        if self.check_record(record_name):
            try:
                to_change = {}
                to_change[attr] = new_value
                self.reduce_record(record_name, attr)
                self.extend_record(record_name, **to_change)
            except(Exception):
                print('Error when changing {} for {}'.format(attr, record_name))
        else:
            print('Could not change {}, no such record'.format(record_name))

    def check_record_attr(self, record_name, attr):
        """Checks the value of an attribute for a record"""
        if self.check_record(record_name):
            record = self.fetch_record(record_name)
            try:
                return getattr(record, attr)
            except(Exception):
                print('Error when checking {} of {}'.format(attr, record))
        else:
            print('Could not check {}, no such record'.format(record_name))

    def list_record_info(self, record):
        """Lists all current attributes and their values"""
        if self.check_record(record):
            with shelve.open(self.db_name) as db:
                try:
                    #for attr,value in db[record].__dict__.items():
                        #print('value of {} is {}'.format(attr,value))
                    return db[record].__dict__.items()
                except(Exception):
                    print('Could not list info for {}'.format(record))
        else:
            print('Could not list info for {}, no such record'.format(record))

    def print_record_info(self, record):
        """Convenience function"""
        for attr,value in self.list_record_info:
            print('value of {} is {}'.format(attr,value))

