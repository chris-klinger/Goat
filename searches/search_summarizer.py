"""
Module explanation
"""

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
    def __init__(self, *args):
        pass

class SearchResult:
    """
    Generic object representing the actual summarized result for a given
    query in a given database. At minimum, should include the result of
    the search (positive/negative). In the case of positive results,
    should have one or more objects representing each positive hit.
    """
    def __init__(self, *args):
        pass

class PositiveHit:
    """
    Class representing a positive hit from a search. Should include
    various attributes of the forward and reverse hits themselves,
    such as specific evalues, etc.
    """
    def __init__(self, *args):
        pass

def summarize_one_result(result_name=None, min_evalue_threshold=None,
    next_hit_evalue_threshold=None):
    """
    Summarizes one single search, based on cutoff criteria. For now, this
    will just be an evalue cutoff, and optionally, though nonsensically,
    a cutoff between hits that would otherwise be positive. I.e. if the
    first four hits match the evalue criteria, but hit 3 has an evalue at
    least better than <next_hit_evalue_threshold> over hit 4, hit 4 will
    not be included in the summary.
    """
    pass

def summarize_two_results(fwd_result=None, rev_result=None,
    min_fwd_evalue_threshold=None, min_rev_evalue_threshold=None,
    next_hit_evalue_threshold=None):
    """
    Summarizes two searches, one representing the forward search and the
    other representing the reverse search. In this case, hits can be
    limited by an evalue cutoff in both directions, and between hits.
    """
    pass
