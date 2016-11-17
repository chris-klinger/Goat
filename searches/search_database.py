"""
This module holds code to store the results of a search. The database itself
consists of a number of records. Each record consists of information regarding
the query (a pointer to the original query object?), the database (pointer
to the database file?), and the parsed output from the search as a stored
object. In this way, it should be easy to use the information in this DB to
execute further searches, obtain results, or any other possible application.
"""

import shelve

class Result:
    """
    A class modeling an individual query/database result from a search.
    Should include attributes as pointers to keep track of both query
    and database information, as well as another attribute which
    represents the parsed output file object for persistence even in
    the absence of the file
    """
    def __init__(self, identity, query=None, database=None, location=None,
            qtype=None, record=None):
        self.identity = identity
        self.query = query
        self.database = database
        self.location = location
        self.qtype = qtype
        self.record = record

class ResultsDB:
    """Abstracts the underlying shelve database"""
    def __init__(self, db_name):
        self.db_name = db_name

    def check_result(self, result_name):
        """Checks whether a query is present"""
        for entry in self.list_results():
            if entry == result_name:
                return True
        return False

    def list_results(self):
        """Utility function"""
        with shelve.open(self.db_name) as db:
            return list(db.keys())

    def fetch_result(self, result_name):
        """Fetches a query"""
        with shelve.open(self.db_name) as db:
            return db[result_name]

    def update_result(self, result_name, result):
        """Stores back a query"""
        with shelve.open(self.db_name) as db:
            db[result_name] = result

    def add_result(self, result_name, **kwargs):
        """Adds information to already existing records"""
        with shelve.open(self.db_name) as db:
            db[result_name] = Result(result_name)
        if len(kwargs) > 0:
            self.add_result_info(result_name, **kwargs)

    def add_result_info(self, result_name, **kwargs):
        """Adds information to pre-existing records"""
        if self.check_result(result_name):
            result = self.fetch_result(result_name)
            for attr,value in kwargs.items():
                try:
                    setattr(result, attr, value)
                except(Exception):
                    print('Error when adding value {} to record {}'.format(attr, result))
            self.update_result(result_name, result)
        else:
            print('Could not extend {}, no such record'.format(result_name))
