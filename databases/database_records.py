"""
This module contains code to work with records

Note: will need to determine how best to implement these functions together
with the underlying shelve database and record class... for now, this will
serve as a reminder of required functionality!
"""

def check_record(record=None):
    """Checks whether a record is present"""
    pass

def add_record_obj(record=None, **kwargs):
    """Adds information to already existing records"""
    pass

def remove_record_obj(record=None):
    """Removes a record from the database"""
    pass

def extend_record(record=None, **kwargs):
    """Adds information to pre-existing records"""
    pass

def reduce_record(record=None, **kwargs):
    """Removes information from pre-existing records"""
    pass

def change_record_attr(record=None, attr=None, new_value=None):
    """Changes one or more attributes of a record"""
    pass

def list_record_info(record=None):
    """Lists all current attributes and their values"""
    pass
