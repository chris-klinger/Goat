"""
This module contains code for query objects in Goat. Each query object has
an associated identity (i.e. what the query would be known as colloquially),
an associated file, which may have more than one query sequence in it, and
may also have other attributes such as an associated database entry, and
one or more redundant accessions - these represent other entries in the
database which can be counted as "the same" sequence for the purposes of
determining whether a reverse search actually retrieves the original
query or not.
"""

import shelve

class Query():
    """Generic Query class"""
    def __init__(self, identity, name=None, description=None, location=None,
            qtype=None, sequence=None, record=None, redundant_accs=None):
        self.identity = identity
        self.name = name
        self.description = description
        self.location = location
        self.qtype = qtype
        self.sequence = sequence
        self.record = record
        self.redundant_accs = redundant_accs

    def get_redundant_accs(self):
        """
        Should define a function that allows for retrieval of redundant
        accessions, either manually or automatically through some kind of
        cutoff criteria. Either way, needs to carry out a query vs. self
        search and analyze the results to determine presence/absence of
        orthologues in the database
        """
        pass

class QueryDB:
    """Abstracts underlying shelve database"""
    def __init__(self, db_name):
        self.db_name = db_name

    def check_query(self, query_name):
        """Checks whether a query is present"""
        for entry in self.list_queries():
            if entry == query_name:
                return True
        return False

    def list_queries(self):
        """Utility function"""
        with shelve.open(self.db_name) as db:
            return list(db.keys())

    def fetch_query(self, query_name):
        """Fetches a query"""
        with shelve.open(self.db_name) as db:
            return db[query_name]

    def update_query(self, query_name, query):
        """Stores back a query"""
        with shelve.open(self.db_name) as db:
            db[query_name] = query

    def add_query(self, query_name, **kwargs):
        """Adds information to already existing records"""
        with shelve.open(self.db_name) as db:
            db[query_name] = Query(query_name)
        if len(kwargs) > 0:
            self.add_query_info(query_name, **kwargs)

    def add_query_info(self, query_name, **kwargs):
        """Adds information to pre-existing records"""
        if self.check_query(query_name):
            query = self.fetch_query(query_name)
            for attr,value in kwargs.items():
                try:
                    setattr(query, attr, value)
                except(Exception):
                    print('Error when adding value {} to record {}'.format(attr, query))
            self.update_query(query_name, query)
        else:
            print('Could not extend {}, no such record'.format(query_name))
