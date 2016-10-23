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
    def __init__(self, query, database, output):
        self.query = query
        self.database = database
        self.output = output

class ResultsDB:
    """Abstracts the underlying shelve database"""
    def __init__(self, db_name):
        self.db_name = db_name

    def list_records(self):
        """Utility function"""
        with shelve.open(self.db_name) as db:
            return list(db.keys())

    def fetch_record(self, query, database): # will likely change
        """Fetches a record"""
        with shelve.open(self.db_name) as db:
            return db[query] # will definitely change
