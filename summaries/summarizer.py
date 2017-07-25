"""
This module contains code to summarize things in Goat. To begin, write a class to
summarize one or two searches into a single Summary object. However, in the future,
would also like to write a separate class that can summarize one or more summaries
in order to allow users to see how results for the same query/db pair can change
depending on which search modes/cutoff criteria are used.
"""

from summaries import summary_obj
from searches import search_util

class SearchSummarizer:
    def __init__(self, summary, query_db, search_db, result_db, fwd_search,
            rev_search=None, max_hits=None, fwd_evalue_cutoff=None,
            rev_evalue_cutoff=None, next_hit_evalue_cutoff=None):
        self.summary = summary # actual summary object
        self.qdb = query_db
        self.sdb = search_db
        self.udb = result_db
        self.fwd_search = fwd_search # name only
        self.rev_search = rev_search # name only
        self.max_hits = max_hits
        self.fwd_evalue = fwd_evalue_cutoff
        self.rev_evalue = rev_evalue_cutoff
        self.next_evalue = next_hit_evalue_cutoff

    def summarize_one_result(self):
        """Summarizes one (forward) search based on basic evalue criteria"""
        fwd_sobj = self.sdb[self.fwd_search]
        for uid in fwd_sobj.list_results():
            fwd_uobj = self.udb[uid]
            qid = fwd_uobj.query
            if self.summary.check_query_summary(qid): # is present already
                query_sum = self.summary.fetch_query_summary(qid)
            else:
                query_sum = summary_obj.QuerySummary(qid)
            self.add_forward_result_summary(fwd_uobj, query_sum)

    def add_forward_result_summary(self, fwd_uobj, query_sum):
        """Returns hits for forward search"""
        result_sum = summary_obj.ResultSummary(fwd_uobj.database)
        if not self.check_parsed_output(fwd_uobj):
            pass # freak out
        hit_list = fwd_uobj.parsed_result.descriptions
        self.add_forward_hits(hit_list, result_sum)
        query_sum.add_db_summary(result_sum)

    def add_forward_hits(self, fwd_hit_list, result_sum):
        """Returns hits for forward search"""
        hit_index = 0
        for desc in fwd_hit_list: # BLAST only, change eventually!
            hit_status = 'negative'
            if (hit_index == self.max_hits) or (desc.e > self.fwd_evalue):
                break # either condition signals end of looking for hits
            if self.next_evalue is None: # any hits automatically true
                hit_status = 'positive'
            else: # we do care about the next hit evalue
                try:
                    next_e = fwd_hit_list[(hit_index + 1)].e
                    if (desc.e + self.next_evalue) < next_e:
                        hit_status = 'positive'
                    else: # still negative!
                        break # stop at first negative hit
                except(IndexError): # no more hits to look at
                    hit_status = 'positive' # there's nothing after it, so must be positive
            if hit_status == 'positive':
                fwd_id = search_util.remove_blast_header(desc.title)
                hit = summary_obj.Hit(fwd_id, desc.e)
                result_sum.add_hit(fwd_id, hit)
        if len(result_sum.positive_hit_list) > 0:
            result_sum.status = 'positive'

    def summarize_two_results(self):
        """Summarize a forward and reverse search together to determine hits
        based on multiple evalue criteria."""
        fwd_sobj = self.sdb[self.fwd_search]
        rev_sobj = self.sdb[self.rev_search]
        for fwd_uid in fwd_sobj.list_results():
            fwd_uobj = self.udb[fwd_uid]
            fwd_qid = fwd_uobj.query
            fwd_qobj = self.qdb[fwd_qid]
            if self.summary.check_query_summary(fwd_qid): # is present already
                query_sum = self.summary.fetch_query_summary(fwd_qid)
            else:
                query_sum = summary_obj.QuerySummary(fwd_qid)
            for rev_uid in rev_sobj.list_results():
                rev_uobj = self.udb[rev_uid]
                rev_qobj = self.qdb[rev_uobj.query]
                if fwd_qobj.identity == rev_qobj.original_query: # rev result originates from original query
                    self.add_reverse_result_summary(fwd_qobj, fwd_uobj, rev_uobj, query_sum)

    def add_reverse_result_summary(self, fwd_qobj, fwd_uobj, rev_uobj, query_sum):
        """Returns hits for reverse search"""
        result_sum = summary_obj.ResultSummary(fwd_uobj.database)
        if not (self.check_parsed_output(fwd_uobj)) or (self.check_parsed_output(rev_uobj)):
            pass # freak out
        fwd_hits = fwd_uobj.parsed_result.descriptions
        self.add_reverse_hits(fwd_qobj, fwd_hits, rev_uobj, result_sum)
        if len(result_sum.positive_hit_list) > 0:
            result_sum.status = 'positive'
        elif len(result_sum.tentative_hit_list) > 0:
            result_sum.status = 'tentative'
        elif len(result_sum.unlikely_hit_list) > 0:
            result_sum.status = 'unlikely'

    def add_reverse_hits(self, fwd_qobj, fwd_hit_list, rev_uobj, result_sum):
        """Returns hits for reverse search"""
        for fwd_hit in fwd_hit_list:
            if (self.fwd_evalue is None) or (fwd_hit.e < self.fwd_evalue):
                if rev_uobj.query in fwd_hit.title: # matching hit/reverse search pair
                    rev_hits = rev_uobj.parsed_result.descriptions
                    status,pos_hit,neg_hit = self.reverse_hit_status(fwd_qobj, rev_hits)
                    fwd_id = search_util.remove_blast_header(fwd_hit.title)
                    hit = summary_obj.Hit(fwd_id, fwd_hit.e,
                            search_util.remove_blast_header(pos_hit.title), pos_hit.e,
                            search_util.remove_blast_header(neg_hit.title), neg_hit.e,
                            (pos_hit.e - neg_hit.e), status)
                    result_sum.add_hit(fwd_id, hit)

    def reverse_hit_status(self, fwd_qobj, rev_hit_list):
        """Determines the status of a forward hit based on reverse search"""
        status = 'negative'
        first_hit_positive = False
        last_hit_positive = False
        first_positive_hit = False
        first_negative_hit = False
        if not self.max_hits:
            max_hits = len(rev_hit_list)
        rev_hit_index = 0
        for rev_hit in rev_hit_list:
            #print(rev_hit)
            if (rev_hit_index == max_hits) or (rev_hit.e > self.rev_evalue):
                break # both of these conditions means we don't need to look more
            new_title = search_util.remove_blast_header(rev_hit.title)
            if (new_title == fwd_qobj.identity) or (new_title in fwd_qobj.redundant_accs):
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
                    if (self.next_evalue is None) or ((first_positive_hit.e -\
                    rev_hit.e) < self.next_evalue):
                        status = 'positive'
                    else:
                        status = 'tentative'
                    break # status determined
                elif last_hit_positive: # first hit wasn't a match but we did find one
                    if self.next_evalue is None or ((first_negative_hit.e -\
                    rev_hit.e) < self.next_evalue):
                        status = 'unlikely'
                    else:
                        status = 'negative'
                    break
                else:
                    pass
            rev_hit_index += 1
        return (status, first_positive_hit, first_negative_hit)

    def check_parsed_output(self, uobj):
        """Returns True if parsed output exists"""
        if uobj.parsed_result:
            return True
        else:
            try:
                pass # need to put in clause to parse output file here
            except:
                pass # Again, need to throw error, etc.
        return False # If all else fails, warn user
