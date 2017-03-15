"""
This module contains utility code associated with searching operations
in Goat.
"""

import os,re

from Bio.Blast import NCBIXML

from databases import database_config
from searches import search_summarizer
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
    valids = ['record','redundant_accs']
    loop = True
    while loop is True:
        attr = prompts.LimitedPrompt(
            message = 'Please choose either "record" or "accessions"',
            errormsg = 'Invalid choice',
            valids = valids).prompt()
        if attr == 'record':
            value = prompts.RecordPrompt(
                message = 'Please choose a record').prompt()
        elif attr == 'redundant_accs':
            value = prompts.LimitedPrompt(
                message = 'How to add accessions? [manual,auto]',
                errormsg = 'Invalid choice',
                valids = ['manual','auto']).prompt()
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

def parse_output_file(filepath, filetype='BLAST'):
    """
    Invokes a parser to parse the given filetype and returns the parsed
    object. In future, may even make this so that the function can guess
    at the filetype if it is not provided.
    """
    if filetype == 'BLAST':
        # note, for now still using 'read' instead of 'parse'
        result_obj = NCBIXML.read(open(filepath))
    else:
        pass # need to implement
    return result_obj

# Likely to be removed
def return_positive_hits(fwd_hit_list, rev_result_list=None, min_fwd_evalue_threshold=None,
        min_rev_evalue_threshold=None, next_hit_evalue_threshold=None, original_query=None):
    """Determines positive hits from one or two lists depending on criteria"""
    positive_hits = []
    if rev_result_list is None:
        hit_index = 0
        for hit in fwd_hit_list:
            if min_fwd_evalue_threshold is None and next_hit_evalue_threshold is None:
                positive_hits.append([hit.title,hit.e])
            elif min_fwd_evalue_threshold is not None and next_hit_evalue_threshold is None:
                if hit.e < min_fwd_evalue_threshold:
                    positive_hits.append([hit.title,hit.e])
            elif min_fwd_evalue_threshold is None and next_hit_evalue_threshold is not None:
                if (hit.e + next_hit_evalue_threshold) < fwd_hit_list[hit_index+1].e: # what about index error?
                    positive_hits.append([hit.title,hit.e])
            else:
                if hit.e < min_fwd_evalue_threshold and ((hit.e + next_hit_evalue_threshold) <
                        fwd_hit_list[hit_index+1].e):
                    positive_hits.append([hit.title,hit.e])
            hit_index += 1
    else:
        fwd_hit_index = 0
        #rev_result_index = 0
        for fwd_hit in fwd_hit_list:
            print(fwd_hit)
            if (min_fwd_evalue_threshold is None) or (fwd_hit.e < min_fwd_evalue_threshold):
                #for rev_hit in rev_result_list:
                    #print(rev_hit)
                    #if fwd_hit == rev_result.query: # found a match
                    #rev_hit_index = 0
                rev_hit_index = 0
                for rev_hit in rev_result_list:
                    print(rev_hit)
                    if (rev_hit == original_query) or (rev_hit in original_query.redundant_accs):
                        if min_rev_evalue_threshold is None and next_hit_evalue_threshold is None:
                            positive_hits.append([fwd_hit.title,fwd_hit.e])
                        elif min_rev_evalue_threshold is not None and next_hit_evalue_threshold is None:
                            if rev_hit.e < min_rev_evalue_threshold:
                                positive_hits.append([fwd_hit.title,fwd_hit.e])
                        elif min_rev_evalue_threshold is None and next_hit_evalue_threshold is not None:
                            if (rev_hit.e + next_hit_evalue_threshold) < \
                                    rev_result_list[rev_hit_index+1].e:
                                positive_hits.append([fwd_hit.title,fwd_hit.e])
                        else: # both are 'not None'
                            if (rev_hit.e < min_rev_evalue_threshold) and ((rev_hit.e +\
                            next_hit_evalue_threshold) < (rev_result_list[rev_hit_index+1].e)):
                                positive_hits.append([fwd_hit.title,fwd_hit.e])
                    rev_hit_index += 1
                    #rev_result_index += 1
            fwd_hit_index += 1
    return positive_hits

# Likely to be removed
def return_positive_reverse_hits(fwd_hit, rev_hit_list, min_rev_evalue_threshold=None,
        next_hit_evalue_threshold=None, original_query=None):
    """Determines positive reverse hits"""
    #positive_hits = []
    positive = 'No'
    first_hit_positive = False
    last_hit_positive = False
    rev_hit_index = 0
    for rev_hit in rev_hit_list:
        print(rev_hit)
        # Rev hit is the original query, or something like it
        if (remove_blast_header(rev_hit.title) == original_query.identity) or\
            (remove_blast_header(rev_hit.title) in original_query.redundant_accs):
            print('rev hit looks like the original query')
            if min_rev_evalue_threshold is None or rev_hit.e < min_rev_evalue_threshold:
                print(rev_hit_index)
                if rev_hit_index == 0: # first hit
                    first_hit_positive = True
                    last_hit_positive = True
                    print('first hit is a match!')
                else: # not the first hit, but it is a match
                    last_hit_positive = True
                    print('hit other than the first is a match')
        else: # rev hit does not look like the original query
            #print('rev hit looks nothing like the original query')
            if rev_hit_index == (len(rev_hit_list)-1): # We only found positive hits
                if first_hit_positive:
                    positive = 'Yes'
                else:
                    positive = 'Maybe' # Placeholder for now!
            if last_hit_positive:
                if next_hit_evalue_threshold is None or ((rev_hit_list[rev_hit_index-1].e -\
                    rev_hit.e) > next_hit_evalue_threshold):
                    if first_hit_positive:
                        positive = 'Yes'
                    else:
                        positive = 'Maybe'
        rev_hit_index += 1
    if positive == 'Yes':
        print(fwd_hit.title + ' is positive')
    elif positive == 'Maybe':
        print(fwd_hit.title + ' may be positive')
    else:
        print(fwd_hit.title + ' is negative')
    return positive
    #print('returning positive hits')
    #print(positive_hits)
    #return positive_hits

def determine_reverse_positive(original_query, rev_hit_list, min_rev_evalue_threshold=None,
    next_hit_positive_evalue_cutoff=None, next_hit_negative_evalue_cutoff=None, max_hits=None):
    """Determines whether a forward hit is positive by scanning reverse hits"""
    status = 'negative'
    first_hit_positive = False
    last_hit_positive = False
    first_positive_hit = False
    first_negative_hit = False
    if not max_hits:
        max_hits = len(rev_hit_list)
    rev_hit_index = 0
    for rev_hit in rev_hit_list:
        #print(rev_hit)
        if (rev_hit_index == max_hits) or (rev_hit.e > min_rev_evalue_threshold):
            break # both of these conditions means we don't need to look more
        if (remove_blast_header(rev_hit.title) == original_query.identity) or\
        (remove_blast_header(rev_hit.title) in original_query.redundant_accs):
            if rev_hit_index == (len(rev_hit_list)-1):
                status = 'positive'
                break # we only found positive hits
            if rev_hit_index == 0:
                first_hit_positive = True
            else:
                last_hit_positive = True
            if not first_positive_hit:
                first_positive_hit = rev_hit # store a ref to the first positive hit
        else: # not a match
            if not first_negative_hit:
                first_negative_hit = rev_hit # store a ref to the first negative hit
            if first_hit_positive: # this is the first non-match hit
                if next_hit_positive_evalue_cutoff is None or ((first_positive_hit.e -\
                rev_hit.e) < next_hit_positive_evalue_cutoff):
                    status = 'positive'
                else:
                    status = 'tentative'
                break
            elif last_hit_positive: # first hit wasn't a match but we did find one
                if next_hit_negative_evalue_cutoff is None or ((first_negative_hit.e -\
                rev_hit.e) < next_hit_negative_evalue_cutoff):
                    status = 'unlikely'
                else:
                    status = 'negative'
                break
            else:
                pass
        rev_hit_index += 1
    #print(status)
    #print(first_positive_hit)
    return (status, first_positive_hit)

def get_temporary_outpath(goat_dir, query_name):
    """
    Provides a temporary filepath for a given query file for use in
    determining redundant accessions.
    """
    outdir = os.path.join(goat_dir, 'tmp') # might be replaced by a set tmp directory later
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    return os.path.join(outdir, (str(query_name) + '.txt'))
