"""
This module contains updated code for dealing with query objects in Goat. Idea is
to provide a common set of attributes that all queries possess and then add more
attributes and methods in subclasses to allow different subtypes to be coded in a
representative manner.
"""

from persistent import Persistent

class Query(Persistent):
    """Generic Query class"""
    def __init__(self, identity, name=None, description=None, location=None,
            alphabet=None, sequence=None, target_db=None, original_query=None,
            tag='standard'):
        # standard attributes for all queries
        self.identity = identity
        self.name = name
        self.description = description
        self.location = location
        self.alphabet = alphabet
        self.sequence = sequence
        # attributes for reverse searches
        self.target_db = target_db # if present, name of record
        self.original_query = original_query # if present = qid
        # whether or not to display in main window
        self.tag = tag

class SeqQuery(Query):
    """
    Query object for a single sequence-based query, e.g. for blast or phmmer. Also
    important for providing reverse search information for HMM- and MSA-based
    queries when considering hits and redundant accessions.
    """
    def __init__(self, record=None, racc_mode=None, *args, **kwargs):
        Query.__init__(self, *args, **kwargs)
        self.search_type = 'seq'
        self.record = record # record for running self-search
        self.racc_mode = racc_mode
        self.search_ran = False # to begin
        self.all_accs = []
        self.raccs = [] # redundant_accessions

class HMMQuery(Query):
    """
    HMM object for a single hmm-based query. At minimum, need to provide the file/
    sequence for the HMM (as in base class), but can also choose to add one or more
    query objects (mainly for the raccs), and additionally either sequences or an
    MSA for use in running iterative searches. Need to have a way of making an
    HMM from the input MSA, including when initial query only includes sequences.
    """
    def __init__(self, *args, **kwargs):
        Query.__init__(self, *args, **kwargs)
        self.search_type = 'hmm'
        self.associated_queries = [] # associated qids only!
        self.seqs = [] # list of sequences
        self.seq_file = None
        self.msa = None # msa object
        self.msa_file = None

    def add_query(self, qid):
        """Convenience function"""
        self.associated_queries.append(qid)

class MSAQuery(Query):
    """
    MSA object for a single msa-based query. Like HMM-based queries, should provide
    an option for including queries for raccs (for reverse searches).
    """
    pass
