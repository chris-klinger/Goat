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
import curses

from Bio.Blast import NCBIXML

from databases import database_config
from searches import search_util, get_raccs
from searches.blast import blast_setup

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'

class Query():
    """Generic Query class"""
    def __init__(self, identity, name=None, description=None, location=None,
            search_type=None, db_type=None, sequence=None, target_db=None,
            record=None, redundant_accs=None):
        self.identity = identity
        self.name = name
        self.description = description
        self.location = location
        self.search_type = search_type
        self.db_type = db_type
        self.sequence = sequence
        self.target_db = target_db
        self.record = record
        self.redundant_accs = redundant_accs

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

    def add_redundant_accs(self, goat_dir, query_name):
        """Gets redundant accs by query_name"""
        if self.check_query(query_name):
            query = self.fetch_query(query_name)
            if query.redundant_accs is not None:
                if query.record is None:
                    print('Could not determine redundant accs for {}, no associated record'.format(query_name))
                else:
                    target_db = database_config.get_record_attr(goat_dir,
                        query.db_type, query.record)
                    #print(target_db)
                    outpath = search_util.get_temporary_outpath(goat_dir, query_name)
                    #print(outpath)
                    #print(query.db_type)
                    if query.db_type == 'protein':
                        blast_search = blast_setup.BLASTp(blast_path, query, target_db, outpath)
                    elif query.db_type == 'genomic':
                        pass
                    blast_search.run_from_stdin()
                    if query.redundant_accs == 'manual':
                        raccs = get_raccs.add_redundant_accs_manual(outpath) # call some other function
                        print(raccs)
                    elif query.redundant_accs == 'auto':
                        pass # call some other function
            self.add_query_info(query_name, redundant_accs=raccs)
        else:
            print('Could not get accs for {}, no such record'.format(query_name))


