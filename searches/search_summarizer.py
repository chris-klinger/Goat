"""
Module explanation
"""

import shelve
from searches import search_database, search_util
from util.inputs import prompts

class Summary:
    """
    Generic summary object. One object should exist for each individual
    query in the initial search. Attributes should include, at least:
        -various query attributes
        -fwd search type
        -rev search type (if applicable)
        -list of databases searched in
        -cutoff criteria applied
    Each entry in the database list should include a separate class.
    Interaction is through a separate class.
    """
    def __init__(self, query, fwd_result_name=None, fwd_search_type=None,
            rev_result_name=None, rev_search_type=None,
            min_fwd_evalue_threshold=None, min_rev_evalue_threshold=None,
            next_hit_evalue_threshold=None):
        self.query = query
        self.databases = [] # initialize an empty list, should this be part of constructor?
        self.fwd_result_name = fwd_result_name
        self.fwd_search_type = fwd_search_type
        self.rev_result_name = rev_result_name
        self.rev_search_type = rev_search_type
        self.min_fwd_evalue_threshold = min_fwd_evalue_threshold
        self.min_rev_evalue_threshold = min_rev_evalue_threshold
        self.next_hit_evalue_threshold = next_hit_evalue_threshold

    def add_search_result(self, result_database):
        """Adds a search result to the Summary"""
        self.databases.append(SearchResult(result_database))

    def get_search_result(self, result_database):
        """Fetches a SearchResult object"""
        for db in self.databases:
            if db.database == result_database:
                return db

class SearchResult:
    """
    Generic object representing the actual summarized result for a given
    query in a given database. At minimum, should include the result of
    the search (positive/negative). In the case of positive results,
    should have one or more objects representing each positive hit.
    """
    def __init__(self, database):
        self.database = database
        self.positive = False # assume not positive to start
        self.positive_hits = [] # initialize an empty list

    def add_positive_hit(self, *args):
        """Adds a positive hit to the SearchResult"""
        self.positive_hits.append(PositiveHit(*args))
        if not self.positive:
            self.positive = True # one or more positive hits indicates positive result

    def num_positive_hits(self):
        """On the fly lookup"""
        return len(self.positive_hits)

class PositiveHit:
    """
    Class representing a positive hit from a search. Should include
    various attributes of the forward and reverse hits themselves,
    such as specific evalues, etc.
    """
    def __init__(self, fwd_hit_identity, fwd_hit_evalue, hit_status,
            rev_hit_identity=None, rev_hit_evalue=None, *args): # can we add even more information?
        self.fwd_hit_identity = fwd_hit_identity
        self.fwd_hit_evalue = fwd_hit_evalue
        self.hit_status = hit_status
        self.rev_hit_identity = rev_hit_identity
        self.rev_hit_evalue = rev_hit_evalue

def summarize_one_result(summary_name, result_name=None, **kwargs):
    """
    Summarizes one single search, based on cutoff criteria. For now, this
    will just be an evalue cutoff, and optionally, though nonsensically,
    a cutoff between hits that would otherwise be positive. I.e. if the
    first four hits match the evalue criteria, but hit 3 has an evalue at
    least better than <next_hit_evalue_threshold> over hit 4, hit 4 will
    not be included in the summary.
    """
    if result_name is None:
        result_name = prompts.StringPrompt(
            message = 'Please input a valid db name').prompt()
    summary_db = SummaryDB(summary_name)
    result_db = search_database.ResultsDB(result_name)
    for result in result_db.list_results():
        if summary_db.check_summary(result.query): # does the entry already exist?
            summary_obj = summary_db.fetch_summary(result.query)
            search_result = summary_obj.add_search_result(result.database)
            for positive_hit in search_util.return_positive_hits(search_result.parsed_obj.descriptions):
                search_result.add_positive_hit(*positive_hit)
        else:
            summary_db.add_summary(result.query)
            summary_obj = summary_db.fetch_summary(result.query)
            search_result = summary_obj.add_search_result(result.database)
            for positive_hit in search_util.return_positive_hits(search_result.parsed_obj.descriptions):
                search_result.add_positive_hit(*positive_hit)

def summarize_two_results(summary_name, fwd_result_name=None, rev_result_name=None,
    min_fwd_evalue_threshold=None, min_rev_evalue_threshold=None,
    next_hit_evalue_threshold=None):
    """
    Summarizes two searches, one representing the forward search and the
    other representing the reverse search. In this case, hits can be
    limited by an evalue cutoff in both directions, and between hits.
    """
    if fwd_result_name is None:
        fwd_result_name = prompts.StringPrompt(
            message = 'Please input a valid fwd db name').prompt()
    if rev_result_name is None:
        rev_result_name = prompts.StringPrompt(
            message = 'Please input a valid rev db name').prompt()
    summary_db = SummaryDB(summary_name)
    fwd_result_db = search_database.ResultsDB(fwd_result_name)
    rev_result_db = search_database.ResultsDB(rev_result_name)
    for fwd_result in fwd_result_db.list_results():
        print(str(fwd_result))
        fwd_result_obj = fwd_result_db.fetch_result(fwd_result)
        print(str(fwd_result_obj.query.identity))
        if summary_db.check_summary(fwd_result_obj.query.identity):
            summary_obj = summary_db.fetch_summary(fwd_result_obj.query)
            search_result = summary_obj.add_search_result(fwd_result_obj.database)
            for rev_result in rev_result_db.list_results():
                print('additional hit ' + str(rev_result))
                rev_result_obj = rev_result_db.fetch_result(rev_result)
                if rev_result_obj.query.original_query == fwd_result_obj.query: # matching pair of results
                    for positive_hit in search_util.return_positive_hits(
                        search_result.parsed_obj.descriptions,
                        rev_result_obj.parsed_obj.descriptions):
                            print(positive_hit)
                            search_result.add_positive_hit(*positive_hit)
        else:
            summary_db.add_summary(fwd_result_obj.query.identity, fwd_result_name=fwd_result_name,
                    fwd_search_type=fwd_result_obj.qtype)
            summary_obj = summary_db.fetch_summary(fwd_result_obj.query.identity)
            print(summary_obj)
            #search_result = summary_obj.add_search_result(fwd_result_obj.database)
            summary_obj.add_search_result(fwd_result_obj.database)
            result_obj = summary_obj.get_search_result(fwd_result_obj.database)
            print(result_obj)
            for rev_result in rev_result_db.list_results():
                #print(str(rev_result))
                rev_result_obj = rev_result_db.fetch_result(rev_result)
                #print(str(rev_result_obj.query.original_query))
                if rev_result_obj.query.original_query == fwd_result_obj.query.identity: # results match
                    #print('got matching result hit')
                    fwd_hits = search_util.parse_output_file(fwd_result_obj.location).descriptions
                    for fwd_hit in fwd_hits:
                        if (min_fwd_evalue_threshold is None) or (fwd_hit.e < min_fwd_evalue_threshold):
                            if rev_result_obj.query.identity in fwd_hit.title:
                                #print('got matching hit/reverse search pair')
                                rev_hits = search_util.parse_output_file(rev_result_obj.location).descriptions
                                (status,rev_hit) = (search_util.determine_reverse_positive(fwd_result_obj.query,
                                rev_hits, min_rev_evalue_threshold, next_hit_evalue_threshold,
                                next_hit_evalue_threshold,10))
                                if status != 'negative':
                                    print('adding positive hit')
                                    result_obj.add_positive_hit(fwd_hit.title, fwd_hit.e, status,
                                        rev_hit.title, rev_hit.e)
            summary_db.update_summary(fwd_result_obj.query.identity, summary_obj)
        # Uncomment for testing
        #for summary in summary_db.list_summaries():
            #print(summary)
            #sum_obj = summary_db.fetch_summary(summary)
            #for result in sum_obj.databases:
                #print(result.database)
                #for hit in result.positive_hits:
                    #print(hit)

class SummaryDB:
    """Abstracts the underlying shelve database"""
    def __init__(self, db_name):
        self.db_name = db_name

    def check_summary(self, summary_name):
        """Checks whether a query is present"""
        for entry in self.list_summaries():
            if entry == summary_name:
                return True
        return False

    def list_summaries(self):
        """Utility function"""
        with shelve.open(self.db_name) as db:
            return list(db.keys())

    def fetch_summary(self, summary_name):
        """Fetches a query"""
        with shelve.open(self.db_name) as db:
            return db[summary_name]

    def update_summary(self, summary_name, result):
        """Stores back a query"""
        with shelve.open(self.db_name) as db:
            db[summary_name] = result

    def add_summary(self, summary_name, **kwargs):
        """Adds information to already existing records"""
        with shelve.open(self.db_name) as db:
            db[summary_name] = Summary(summary_name)
        if len(kwargs) > 0:
            self.add_summary_info(summary_name, **kwargs)

    def add_summary_info(self, summary_name, **kwargs):
        """Adds information to pre-existing records"""
        if self.check_summary(summary_name):
            summary = self.fetch_summary(summary_name)
            for attr,value in kwargs.items():
                try:
                    setattr(summary, attr, value)
                except(Exception):
                    print('Error when adding value {} to record {}'.format(attr, summary))
            self.update_summary(summary_name, summary)
        else:
            print('Could not extend {}, no such record'.format(summary_name))


