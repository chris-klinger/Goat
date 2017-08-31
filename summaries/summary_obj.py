"""
This module contains code for summary objects. Summary objects will be implemented
as nested persistent objects:
    -Summary
        -QuerySummary
            -ResultSummary
                -Hit
This nesting will allow a single coherent object to encapsulate the large amount of
data generated by one or two searches in a single object, and traversal through
these objects to generate either graphical or tabular output.
"""

from persistent import Persistent
from BTrees.OOBTree import OOBTree

class Summary(Persistent):
    """
    Root object in the summary scheme, mainly used as a container to hold all
    other information. For each query in the search, the identity of the query
    is appended to the internal list, and the nested substructure is placed
    in a OOBTree container; paired datastructure allows for maintaining order
    and fast lookup by id in an unstructured container.
    """
    def __init__(self, fwd_search, fwd_qtype, fwd_dbtype, fwd_algorithm,
            fwd_evalue_cutoff=None, fwd_max_hits=None,
            rev_search=None, rev_qtype=None, rev_dbtype=None, rev_algorithm=None,
            rev_evalue_cutoff=None, rev_max_hits=None,
            next_hit_evalue_cutoff=None, mode='result'):
        self.query_list = [] # list maintains order
        self.queries = OOBTree()
        self.fwd = fwd_search
        self.fwd_qtype = fwd_qtype
        self.fwd_dbtype = fwd_dbtype
        self.fwd_algorithm = fwd_algorithm
        self.fwd_evalue = fwd_evalue_cutoff # should be a float!
        self.fwd_max_hits = fwd_max_hits
        self.rev = rev_search
        self.rev_qtype = rev_qtype
        self.rev_dbtype = rev_dbtype
        self.rev_algorithm = rev_algorithm
        self.rev_evalue = rev_evalue_cutoff # should be a float!
        self.rev_max_hits = rev_max_hits
        self.next_evalue = next_hit_evalue_cutoff # should be a whole value, e.g. 2, but convert to float
        self.mode = mode # either 'result' or 'summary'

    def check_query_summary(self, qid):
        """Checks whether a QuerySummary object for a given qid already exists"""
        if qid in self.query_list:
            return True
        return False

    def fetch_query_summary(self, qid):
        """Returns the object for the given qid"""
        return self.queries[qid]

    def add_query_summary(self, qid, qsummary):
        """Adds a nested object; qid is appended to list"""
        if not qid in self.query_list:
            self.query_list.append(qid)
            self._p_changed = 1 # signals list was updated
        self.queries[qid] = qsummary # add to internal structure

class QuerySummary(Persistent):
    """
    Object representing each query in the original search. For each database
    searched in, a separate nested object will hold information on whether or
    not homologues were found, and each individual hit.
    """
    def __init__(self, qid):
        self.db_list = []
        self.dbs = OOBTree()
        self.qid = qid

    def check_db_summary(self, db):
        """Checks whether a ResultSummary for the given db already exists"""
        if db in self.db_list:
            return True
        return False

    def fetch_db_summary(self, uid):
        """Returns the object for the given qid"""
        return self.dbs[uid]

    def add_db_summary(self, db, db_summary):
        """Adds a nested object"""
        if not db in self.db_list:
            self.db_list.append(db)
            self._p_changed = 1
        self.dbs[db] = db_summary

class ResultSummary(Persistent):
    """
    Simple object representing the overall result of searching the given DB with
    the given query; status and hits are provided.
    """
    def __init__(self, database):
        self.db = database
        self.status = 'negative'
        self.positive_hit_list = []
        self.tentative_hit_list = []
        self.unlikely_hit_list = []
        self.lists = ['positive_hit_list','tentative_hit_list','unlikely_hit_list']
        self.hits = OOBTree()
        self._determined = False # whether or not the status has been determined

    def determined(self, status=None):
        """Called with no args to check the value of self._determined, called with
        one arg to set that value"""
        if not status:
            return self._determined
        else:
            self.status = status
            self._determined = True

    def add_hit(self, hit_id, hit, status='positive'):
        """Adds a hit (positive or tentative) to the appropriate internal list;
        all hit objects are also added to the tree"""
        if status == 'positive':
            self.positive_hit_list.append(hit_id)
        elif status == 'tentative':
            self.tentative_hit_list.append(hit_id)
        else:
            self.unlikely_hit_list.append(hit_id)
        self._p_changed = 1
        self.hits[hit_id] = hit

class Hit(Persistent):
    """
    Simple object representing a hit in a search; hits may or may not have reverse
    information as well, and will be either 'positive' or 'tentative'.
    """
    def __init__(self, fwd_hit_id, fwd_hit_evalue, # forward info
            pos_rev_hit_id=None, pos_rev_hit_evalue=None, # first positive reverse hit
            neg_rev_hit_id=None, neg_rev_hit_evalue=None, # first negative reverse hit
            rev_hit_evalue_difference=None, # difference between rev evalues
            status='positive'): # assume positive (most hits are)
        self.fwd_id = fwd_hit_id
        self.fwd_evalue = fwd_hit_evalue
        self.pos_rev_id = pos_rev_hit_id
        self.pos_rev_evalue = pos_rev_hit_evalue
        self.neg_rev_id = neg_rev_hit_id
        self.neg_rev_evalue = neg_rev_hit_evalue
        self.rev_evalue_diff = rev_hit_evalue_difference
        self.status = status

#######################################################
# Additional class for summarizing multiple summaries #
#######################################################

class ResultfromSummaries(Persistent):
    """
    Replaces other classes when summarizing multiple summaries; Instead of going
    by hits for each status, holds a separate object for each hit ID. This then
    tracks the status of the hit from each summary (without associated detailed
    info). The overall status of the result is still tracked based on the boolean
    value of the associated hit(s) status.
    """
    def __init__(self, database):
        self.db = database
        self.status = 'negative'
        self.hit_list = []
        self.hits = OOBTree()
        self._determined = False # whether or not the status has been determined

    def determined(self, status=None):
        """Called with no args to check the value of self._determined, called with
        one arg to set that value"""
        if not status:
            return self._determined
        else:
            self.status = status
            self._determined = True

    def get_hit(self, hit_id):
        """
        Checks to see if hit_id is already present and returns the object if so;
        else creates hit and returns the object.
        """
        if hit_id in self.hits.keys():
            return self.hits[hit_id]
        else:
            self.hit_list.append(hit_id)
            self._p_changed = 1
            hit = HitfromSummaries()
            self.hits[hit_id] = hit
            return hit

    def determine_status(self):
        """Checks status of all hits"""
        for hit_id in self.hit_list:
            hit_obj = self.hits[hit_id]
            if hit_obj.status == 'positive':
                self.status = 'positive'
                break # stop as soon as it is positive
            elif hit_obj.status == 'tentative':
                self.status = 'tentative' # always the next best option
            elif hit_obj.status == 'unlikely':
                if not self.status == 'tentative': # only set if not already better
                    self.status = 'unlikely'

class HitfromSummaries(Persistent):
    """
    Class to model the resulting status of each hit based on multiples summaries.
    For each, add the summary name to the status for which the hit falls into for
    that summary.
    """
    def __init__(self):
        self.status = 'negative'
        self.positive_hit_list = []
        self.tentative_hit_list = []
        self.unlikely_hit_list = []
        self.lists = ['positive_hit_list','tentative_hit_list','unlikely_hit_list']
        self._determined = False # whether or not the status has been determined

    def determined(self, status=None):
        """Called with no args to check the value of self._determined, called with
        one arg to set that value"""
        if not status:
            return self._determined
        else:
            self.status = status
            self._determined = True

    def add_summary(self, summ_id, status='positive'):
        """Adds a summary to the relevant list for the hit."""
        if status == 'positive':
            self.positive_hit_list.append(summ_id)
        elif status == 'tentative':
            self.tentative_hit_list.append(summ_id)
        else:
            self.unlikely_hit_list.append(summ_id)
        self._p_changed = 1

    def determine_status(self):
        """
        Called each time through the summarizer loop, checks the length of each
        list and changes the status to match.
        """
        if len(self.positive_hit_list) > 0:
            self.status = 'positive'
        elif len(self.tentative_hit_list) > 0:
            self.status = 'tentative'
        elif len(self.unlikely_hit_list) > 0:
            self.status = 'unlikely'
