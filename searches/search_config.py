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

from databases import database_config
from searches.search_setup import Search, SearchFile
from searches import search_util,search_query,search_database,search_results,search_summarizer
from util.inputs import prompts

def get_search_file(search_dir, search_name):
    """Retrieves the search object in question"""
    search_file = search_name + '.pkl'
    return os.path.join(search_dir, search_name, search_file)

def make_search_file(search_dir, search_name, search_type=None,
        queries=None, databases=None, db_type=None, keep_output=False,
        output_location=None, *params):
    """Makes the search file to hold relevant data"""
    search_file_path = get_search_file(search_dir, search_name)
    with open(search_file_path, 'wb') as o:
        search = Search(search_type, queries, databases, db_type,
                keep_output, output_location, *params)
        pickle.dump(search, o)
    return search_file_path

def get_query_db(search_dir, search_name):
    """Gets the query database for the search"""
    db_file = search_name + '_queryDB'
    return search_query.QueryDB(os.path.join(search_dir, search_name, db_file))

def get_results_db(search_dir, search_name):
    """Gets the result database for the search"""
    db_file = search_name + '_resultsDB'
    return search_database.ResultsDB(os.path.join(search_dir, search_name, db_file))

def new_search(goat_dir, search_name=None, search_type=None, db_type=None,
        target_dir=None, queries=None, databases=None):
    """
    Initiates the process of setting up a new search. New searches are
    named, and require one or more query files, which themselves may have
    one or more queries, one or more databases, and can specify additional
    parameters as needed.
    """
    if search_name is None:
        search_name = search_util.name_file('search')
    if search_type is None:
        search_type = search_util.get_search_type()
    if db_type is None:
        db_type = search_util.get_db_type()
    if target_dir is None:
        use_current_dir = prompts.YesNoPrompt(
            message = 'Do you want to use the current directory for this search?').prompt()
        if use_current_dir.lower() in {'yes','y'}:
            target_dir = os.getcwd()
        else:
            print("Using other directory for search")
            target_dir = search_util.specify_search_dir()
    os.mkdir(os.path.join(target_dir, search_name))
    query_db = get_query_db(target_dir, search_name)
    result_db = get_results_db(target_dir, search_name)
    if not queries:
        # May eventually want to update this to be similar to the
        # interface for adding files for database records
        add_queries_to_search(goat_dir, query_db, search_type, db_type)
    if not databases:
        databases = add_databases_to_search(goat_dir, db_type)
    keep_output_files = prompts.YesNoPrompt(
        message = 'Do you want to keep the output files from this search?').prompt()
    if keep_output_files.lower() in {'yes','y'}:
        keep_output = True
        output_location = search_util.get_output_dir(target_dir, search_name)
    elif keep_output_files.lower() in {'no','n'}:
        keep_output = False
        output_location = search_util.get_output_dir(goat_dir, 'tmp')
    search_file = make_search_file(target_dir, search_name, search_type,
            query_db, databases, db_type, keep_output, output_location, result_db)
    search = SearchFile(search_file)
    #search.run()
    #search.execute()
    search.run_all() # for now, not using execute to avoid parsing output

def search_from_result(goat_dir, result_name=None, search_name=None, search_type=None,
        db_type=None, target_dir=None, queries=None, databases=None):
    """
    Executes a search based on a previous result db. Adds a new query for each
    hit in the result's 'parsed_obj' attribute and then runs the search. User has
    the option to execute a reverse search (requires that the original query has
    an associated 'record' attribute), or a search into one or more other DB's
    """
    reverse_search = False
    pick_dbs = prompts.LimitedPrompt(
            message = 'Reverse search or separate db?',
            errormsg = 'Uncrecognized action',
            valids = ['reverse','separate']).prompt()
    if pick_dbs == 'reverse':
        reverse_search = True
    if result_name is None:
        result_name = prompts.FilePrompt(
            message = 'Please input a valid db name').prompt()
        result_name = result_name.rsplit('.',1)[0]
        result_name = search_database.ResultsDB(result_name)
    if search_name is None:
        search_name = search_util.name_file('search')
    if search_type is None:
        search_type = search_util.get_search_type()
    if db_type is None:
        db_type = search_util.get_db_type()
    if target_dir is None:
        use_current_dir = prompts.YesNoPrompt(
            message = 'Do you want to use the current directory for this search?').prompt()
        if use_current_dir.lower() in {'yes','y'}:
            target_dir = os.getcwd()
        else:
            print("Using other directory for search")
            target_dir = search_util.specify_search_dir()
    os.mkdir(os.path.join(target_dir, search_name))
    query_db = get_query_db(target_dir, search_name)
    result_db = get_results_db(target_dir, search_name)
    if not queries:
        for result in result_name.list_results():
            result_obj = result_name.fetch_result(result)
            for record in search_results.seqs_from_result(result_obj):
                #print(record)
                #print()
                if reverse_search:
                    try:
                        target_db = database_config.get_record_attr(
                            goat_dir, db_type, result_obj.query.record)
                    except Exception:
                        target_db = None
                    #print(target_db)
                    query_db.add_query(record.id, name=record.name,
                        description=record.description, location=None,
                        qtype=search_type, sequence=record.seq, target_db=target_db)
                else:
                    query_db.add_query(record.id, name=record.name,
                        description=record.description, location=None,
                        qtype=search_type, sequence=record.seq)
    if not databases:
        if not reverse_search:
            databases = add_databases_to_search(goat_dir, db_type)
    keep_output_files = prompts.YesNoPrompt(
        message = 'Do you want to keep the output files from this search?').prompt()
    if keep_output_files.lower() in {'yes','y'}:
        keep_output = True
        output_location = search_util.get_output_dir(target_dir, search_name)
    elif keep_output_files.lower() in {'no','n'}:
        keep_output = False
        output_location = search_util.get_output_dir(goat_dir, 'tmp')
    search_file = make_search_file(target_dir, search_name, search_type,
            query_db, databases, db_type, keep_output, output_location, result_db)
    search = SearchFile(search_file)
    #search.run()
    #search.execute()
    search.run_all() # again, avoid actually adding parsed output to result object

def add_queries_to_search(goat_dir, query_db, search_type, db_type):
    """Adds one or more queries to a search object"""
    query_files = search_util.get_query_files()
    add_annotations = prompts.YesNoPrompt(
        message = 'Do you want to add additional info for these queries?').prompt()
    if add_annotations.lower() in {'yes','y'}:
        add_annotations = True
    else:
        add_annotations = False
    for query_file in query_files:
        parsed_queries = SeqIO.parse(query_file, "fasta") # assumes FASTA, needs to be changed later
        for seq_record in parsed_queries:
            query_db.add_query(seq_record.id, name=seq_record.name,
                description=seq_record.description, location=query_file,
                qtype=search_type, db_type=db_type, sequence=seq_record.seq) # identity of the query
            if add_annotations:
                query_db.add_query_info(seq_record.id, name=seq_record.name,
                    description=seq_record.description, location=query_file,
                    qtype=search_type, db_type=db_type, sequence=seq_record.seq,
                    **search_util.add_query_attribute_loop())
                query_db.add_redundant_accs(goat_dir, seq_record.id) # tries to add redundant accessions

def add_databases_to_search(goat_dir, db_type):
    """Specifies one or more databases to add to a search object"""
    return search_util.get_databases(goat_dir, db_type)

def get_search_results(result_name=None, summary_name=None, output=None,
        outdir=os.getcwd(), outfile=None):
    """
    Retrieves results from a given result database or summary file. Results
    can be output as spreadsheets, graphical displays, or sequence files.
    """
    if result_name is None:
        result_name = prompts.FilePrompt(
            message = 'Please input a valid db name').prompt()
        result_name = result_name.rsplit('.',1)[0]
    if output is None:
        output = prompts.LimitedPrompt(
            message = 'Please choose an output [sequence,spreadsheet]',
            errormsg = 'Unrecognized output',
            valids = ['sequence','spreadsheet']).prompt()
    #if outfile is None:
        #outfile = prompts.StringPrompt(
            #message = 'Please input a valid file name').prompt()
    if output == 'sequence':
        search_results.seqfile_from_result_db(result_name, outdir)

def summarize_search_results(summary_name=None, summary_type=None):
    """
    Summarizes searches from one or more result databases. Cutoff criteria
    depends on whether one or two databases are specified.
    """
    if summary_name is None:
        summary_name = search_util.name_file('summary')
    if summary_type is None:
        summary_type = prompts.LimitedPrompt(
            message = 'Summarize from how many results? [one,two]',
            erromsg = 'Please choose "one" or "two"',
            valids = ['one','two']).prompt()
    add_cutoffs = prompts.YesNoPrompt(
        message = 'Do you want to add evalue cutoff criteria?').prompt()
    if add_cutoffs.lower() in {'yes','y'}:
        add_cutoffs = True
    else:
        add_cutoffs = False
    if summary_type == 'one':
        if add_cutoffs:
            cutoffs = search_util.get_cutoff_values('one')
        search_summarizer.summarize_one_result(**cutoffs)
    elif summary_type == 'two':
        if add_cutoffs:
            cutoffs = search_util.get_cutoff_values('two')
        search_summarizer.summarize_two_results(**cutoffs)
