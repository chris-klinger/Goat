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

class Query():
    """Generic Query class"""
    def __init__(self, identity, location, qtype=None, record=None, redundant_accs=None):
        self.identity = identity
        self.location = location
        self.qtype = qtype
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
