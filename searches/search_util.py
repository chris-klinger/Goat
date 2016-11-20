"""
This module contains utility code associated with searching operations
in Goat.
"""

import os,re

from databases import database_config
from util.inputs import prompts

def name_file(file_type):
    """Prompts user for a name for a search"""
    loop = True
    while loop:
        file_name = prompts.StringPrompt(
            message = 'Please enter a name for this {}'.format(
                file_type)).prompt()
        good_name = prompts.YesNoPrompt(
            message = 'Is this ok?').prompt()
        if good_name.lower() in {'yes','y'}:
            loop = False
        else:
            pass
    return file_name

def get_search_type():
    """
    Prompts user for the type of search. Should eventually involve a more
    sophisticated interface but for now limit to BLAST or HMMer
    """
    loop = True
    valids = ['BLAST', 'HMMer']
    while loop:
        search_type = prompts.LimitedPrompt(
            message = 'Please choose a search type',
            errormsg = 'Unrecognized search type',
            valids = valids).prompt()
        good_type = prompts.YesNoPrompt(
            message = 'Is this ok?').prompt()
        if good_type.lower() in {'yes','y'}:
            loop = False
        else:
            pass
    return search_type

def get_db_type():
    """
    Prompts user for the type of database to be searched against. Should
    eventually involve a more sophisticated interface but for not limit
    to either protein or genomic
    """
    loop = True
    valids = ['protein','genomic']
    while loop:
        db_type = prompts.LimitedPrompt(
            message = 'Please choose target db type',
            errormsg = 'Uncrecognized db type',
            valids = valids).prompt()
        good_type = prompts.YesNoPrompt(
            message = 'Is this ok?').prompt()
        if good_type.lower() in {'yes','y'}:
            loop = False
        else:
            pass
    return db_type

def specify_search_dir():
    """Prompts user for a parent directory for searches"""
    search_dir = prompts.DirPrompt(
        message = 'Please enter a directory to add searches to',
        errormsg = 'Please enter a valid directory').prompt()
    return search_dir

def get_query_files():
    """Prompts user for one or more files containing query sequences"""
    query_files = []
    loop = True
    while loop:
        valids = ['add','quit']
        choice = prompts.LimitedPrompt(
            message = 'Please choose to add a query file or quit',
            errormsg = 'Please choose either "add" or "quit"',
            valids = valids).prompt()
        if choice == 'add':
            qfile = prompts.FilePrompt(
                message = 'Please choose a file with one or more query sequences',
                errormsg = 'Please choose a valid file').prompt()
            query_files.append(qfile)
        elif choice == 'quit':
            loop = False
    return query_files

def get_databases(goat_dir, db_type):
    """Prompts user for one or more databases, checks whether each is valid"""
    records_db = database_config.get_record_db(goat_dir)
    databases = []
    loop = True
    while loop:
        valids = ['add','quit']
        choice = prompts.LimitedPrompt(
            message = 'Please choose to add a database or quit',
            errormsg = 'Please choose an existing database',
            valids = valids).prompt()
        if choice == 'add':
            db = prompts.RecordPrompt(
                message = 'Please type a valid database record').prompt()
            if records_db.check_record(db):
                databases.append(database_config.get_record_attr(
                    goat_dir, db_type, db))
                print('Added {} to search database'.format(db))
            else:
                print('Could not find {} in database'.format(db))
        elif choice == 'quit':
            loop = False
    return databases

def add_query_attribute_loop(add_dict=None):
    """
    Collects key, value pairs from a restricted subset of such possible
    pairs, based on the expected attributes in queries.
    """
    if add_dict is None:
        add_dict = {}
    valids = ['record','accessions']
    loop = True
    while loop is True:
        attr = prompts.LimitedPrompt(
            message = 'Please choose either "record" or "accessions"',
            errormsg = 'Invalid choice',
            valids = valids).prompt()
        if attr == 'record':
            value = prompts.RecordPrompt(
                message = 'Please choose a record').prompt()
        elif attr == 'accessions':
            pass # need to implement redundant accessions somehow
        user_conf = prompts.YesNoPrompt(
            message = 'You have entered {} {}, is this correct?'.format(
                attr,value)).prompt() # again, need to fix this later to make it more general
        if user_conf.lower() in {'yes','y'}:
            add_dict[attr] = value
        elif user_conf.lower() in {'no','n'}:
            print('Attribute {} will not be added'.format(attr))
        cont = prompts.YesNoPrompt(
            message = 'Do you wish to add more attributes?').prompt()
        if cont.lower() in {'yes','y'}:
            pass
        elif cont.lower() in {'no','n'}:
            loop = False
    return add_dict

def get_output_dir(target_dir, search_name, name='output'):
    """Makes and returns path to output location"""
    output = os.path.join(target_dir, search_name, name)
    os.mkdir(output)
    return output

def remove_blast_header(instring):
    """
    Removes BLAST formatting introduced into header line in XML output
    that prevents comparison to the original sequence file.
    """
    return re.sub(r'gnl\|BL_ORD_ID\|\d+ ','', instring)

def get_cutoff_values(summary_type):
    """
    Prompts user for evalue cutoff criteria for summarizing searches. Varies depending
    on the number of results being summarized (one or two). Can probably improve this
    at some point in the future.
    """
    cutoffs = {}
    loop = True
    while loop:
        add_evalue = prompts.YesNoPrompt(
            message = 'Add another evalue criterion?').prompt()
        if add_evalue.lower() in {'yes','y'}:
            if summary_type == 'one':
                possible_cutoffs = ['min_fwd_evalue_threshold',
                        'next_hit_evalue_threshold']
            elif summary_type == 'two':
                possible_cutoffs = ['min_fwd_evalue_threshold',
                    'min_rev_evalue_threshold', 'next_hit_evalue_threshold']
            for k in possible_cutoffs:
                try:
                    cutoffs[k] = get_evalue(k)
                except(Exception):
                    pass
        else:
            loop = False
    return cutoffs

def get_evalue(possible_evalue):
    """Convenience function to get evalues"""
    specify_evalue = prompts.YesNoPrompt(
        message = 'Specify a value for {}?'.format(
                possible_evalue)).prompt()
    if specify_evalue.lower() in {'yes','y'}:
        evalue = float(prompts.StringPrompt(
            message = 'Please enter a value').prompt())
    return evalue

def return_positive_hits(fwd_hit_list, rev_hit_list=None, min_fwd_evalue_threshold=None,
        min_rev_evalue_threshold=None, next_hit_evalue_threshold=None):
    """Determines positive hits from one or two lists depending on criteria"""
    positive_hits = []
    if rev_hit_list is None:
        hit_index = 0
        for hit in fwd_hit_list:
            if min_fwd_evalue_threshold is None and next_hit_evalue_threshold is None:
                positive_hits.append(hit)
            elif min_fwd_evalue_threshold is not None and next_hit_evalue_threshold is None:
                if hit.e < min_fwd_evalue_threshold:
                    positive_hits.append(hit)
            elif min_fwd_evalue_threshold is None and next_hit_evalue_threshold is not None:
                if (hit.e + next_hit_evalue_threshold) < fwd_hit_list[hit_index+1].e: # what about index error?
                    positive_hits.append(hit)
            else:
                if hit.e < min_fwd_evalue_threshold and ((hit.e + next_hit_evalue_threshold) <
                        fwd_hit_list[hit_index+1].e):
                    positive_hits.append(hit)
            hit_index += 1
    else:
        #fwd_hit_index = 0
        #rev_hit_index = 0
        pass # do something
