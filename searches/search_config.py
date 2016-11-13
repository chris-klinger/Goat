"""
This module contains code for implementing searches in Goat. Each search
creates a new subdirectory structure in a user-specified directory (defaults
to cwd if unspecified). Within this subdirectory, a search produces:
    -A Search object, which persists as a pickled file
    -A Shelve object, which stores each individual Query object
    -A Shelve object, which stores each individual DB object(?)
    -A Shelve object, which stores all of the results for each search
    -(Optional) Another subdir, with all the associated output files

Interaction between searches, i.e. for summarizing results from many different
searches or obtaining results based on reciprocal analyses, should rely on the
structure of this subdir.
"""

import os, pickle

from Bio import SeqIO

from searches.search_setup import Search, SearchFile
from searches import search_util, search_query
from util.input import prompts

def get_search_file(search_name):
    """Retrieves the search object in question"""
    return SearchFile(search_name)

def make_search_file(search_dir, search_name):
    """Makes the search file to hold relevant data"""
    search_file = search_name + '.pkl'
    search_file_path = os.path.join(search_dir, search_file)
    with open(search_file_path) as o:
        search = Search()
        pickle.dump(search, o)
    return search_file_path

def get_query_db(search_dir, search_name):
    """Gets the query database for the search"""
    return search_query.QueryDB(os.path.join(search_dir, search_name))

def new_search(goat_dir, search_name=None, target_dir=None,
        queries=None, databases=None):
    """
    Initiates the process of setting up a new search. New searches are
    named, and require one or more query files, which themselves may have
    one or more queries, one or more databases, and can specify additional
    parameters as needed.
    """
    if search_name is None:
        search_name = search_util.name_search()
    if target_dir is None:
        use_current_dir = prompts.YesNoPrompt(
            message = 'Do you want to use the current directory for this search?').prompt()
        if use_current_dir.lower() in {'yes','y'}:
            target_dir = os.getcwd()
        else:
            print("Using other directory for search")
            target_dir = search_util.specify_search_dir()
    os.mkdir(os.path.join(target_dir, search_name))
    search = make_search_file(target_dir, search_name)
    query_db = get_query_db(target_dir, search_name)
    if not queries:
        add_queries_to_search(query_db)
    if not databases:
        add_databases_to_search(goat_dir, search)

def add_queries_to_search(query_db):
    """Adds one or more queries to a search object"""
    query_files = search_util.get_query_files()
    for query_file in query_files:
        parsed_queries = SeqIO.parse(query_file, "fasta") # assumes FASTA, needs to be changed later
        for seq_record in parsed_queries:
            query_db.add_query(seq_record.id, query_file) # identity of the query
            # Add other info?

def add_databases_to_search(goat_dir, db_type, search):
    """Specifies one or more databases to add to a search object"""
    databases = search_util.get_databases(goat_dir, db_type)
    for database in databases:
        search.add_db()
