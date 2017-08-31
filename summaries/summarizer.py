"""
This module contains code to summarize things in Goat. To begin, write a class to
summarize one or two searches into a single Summary object. However, in the future,
would also like to write a separate class that can summarize one or more summaries
in order to allow users to see how results for the same query/db pair can change
depending on which search modes/cutoff criteria are used.
"""

import math

from bin.initialize_goat import configs

from summaries import summary_obj
from searches import search_util

class SearchSummarizer:
    def __init__(self, summary): #, fwd_search,
            #rev_search=None, fwd_max_hits=None, rev_max_hits=None,
            #fwd_evalue_cutoff=None, rev_evalue_cutoff=None, next_hit_evalue_cutoff=None):
        self.summary = summary # actual summary object
        self.qdb = configs['query_db']
        self.sdb = configs['search_db']
        self.udb = configs['result_db']
        self.sqdb = configs['search_queries']
        self.mqdb = configs['misc_queries']
        self.fwd_search = summary.fwd #fwd_search # name only
        self.rev_search = summary.rev #rev_search # name only
        self.fwd_max_hits = summary.fwd_max_hits #fwd_max_hits
        self.rev_max_hits = summary.rev_max_hits #rev_max_hits
        self.fwd_evalue = summary.fwd_evalue #fwd_evalue_cutoff
        self.rev_evalue = summary.rev_evalue #rev_evalue_cutoff
        self.next_evalue = summary.next_evalue #next_hit_evalue_cutoff

    def summarize_one_result(self):
        """Summarizes one (forward) search based on basic evalue criteria"""
        fwd_sobj = self.sdb[self.fwd_search]
        for uid in fwd_sobj.list_results():
            fwd_uobj = self.udb[uid]
            db = fwd_uobj.database
            qid = fwd_uobj.query
            if self.summary.check_query_summary(qid): # is present already
                query_sum = self.summary.fetch_query_summary(qid)
            else:
                query_sum = summary_obj.QuerySummary(qid)
            self.add_forward_result_summary(fwd_uobj, db, query_sum)
            self.summary.add_query_summary(qid, query_sum)

    def add_forward_result_summary(self, fwd_uobj, db, query_sum):
        """Returns hits for forward search"""
        if query_sum.check_db_summary(db):
            result_sum = query_sum.fetch_db_summary(db)
        else:
            result_sum = summary_obj.ResultSummary(fwd_uobj.database)
        if not self.check_parsed_output(fwd_uobj):
            pass # freak out
        hit_list = fwd_uobj.parsed_result.descriptions
        self.add_forward_hits(hit_list, result_sum)
        query_sum.add_db_summary(db, result_sum)

    def add_forward_hits(self, fwd_hit_list, result_sum):
        """Returns hits for forward search"""
        hit_index = 0
        for desc in fwd_hit_list: # BLAST only, change eventually!
            hit_status = 'negative'
            if (hit_index == self.fwd_max_hits) or (desc.e > self.fwd_evalue):
                break # either condition signals end of looking for hits
            if self.next_evalue is None: # any hits automatically true
                hit_status = 'positive'
            else: # we do care about the next hit evalue
                try:
                    next_e = math.log(fwd_hit_list[(hit_index + 1)].e, 10)
                    # magnitude difference is greater than specified
                    if math.fabs(math.log(desc.e,10) - next_e) > self.next_evalue:
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
        #print('SEARCH: ' + self.fwd_search)
        fwd_sobj = self.sdb[self.fwd_search]
        #qsobj = self.qdb.fetch_search(self.fwd_search) # Query search object for intermediate results
        rev_sobj = self.sdb[self.rev_search]
        #print(str(rev_sobj.databases))
        for fwd_uid in fwd_sobj.list_results():
            #print('forward result id: ' + fwd_uid)
            fwd_uobj = self.udb[fwd_uid]
            # Check to see if algorithm is 'hmmer'; if so, check to see if spec_qid
            spec_qid = None
            if fwd_uobj.algorithm == 'hmmer':
                if not fwd_uobj.spec_qid:
                    pass # need to warn user and skip result eventually
                else:
                    spec_qid = fwd_uobj.spec_qid
            #print('forward result queries are : ' + str(fwd_uobj.int_queries))
            fwd_qid = fwd_uobj.query
            #print('forward query id: ' + fwd_qid)
            fwd_db = fwd_uobj.database
            fwd_qobj = self.qdb[fwd_qid]
            #print(fwd_qobj.identity)
            #print(fwd_qobj.redundant_accs)
            if self.summary.check_query_summary(fwd_qid): # is present already
                query_sum = self.summary.fetch_query_summary(fwd_qid)
            else:
                query_sum = summary_obj.QuerySummary(fwd_qid)
            #for rev_uid in rev_sobj.list_results():
            for acc in fwd_uobj.int_queries:
                #print("forward acc is " + str(acc))
                for rev_db in rev_sobj.databases:
                    rev_uid = rev_sobj.name + '-' + acc + '-' + rev_db
                    #print('reverse result id: ' + rev_uid)
                    rev_uobj = self.udb[rev_uid]
                    #print('reverse result name is: ' + rev_uobj.name)
                    rev_qobj = self.sqdb[rev_uobj.query]
                    #print(rev_qobj.original_query)
                    # confirms rev search object stems from original query
                    # second line covers profile-based queries
                    if ((fwd_qobj.identity == rev_qobj.original_query) or\
                        (fwd_uobj.spec_qid == rev_qobj.original_query)) and \
                        (rev_uid.split('-')[1] in fwd_uobj.int_queries):
                        #print('reverse result originates from original query')
                        self.add_reverse_result_summary(fwd_qobj, fwd_uobj, rev_uobj,
                                fwd_db, query_sum, spec_qid)
                        #print()
                #print()
            self.summary.add_query_summary(fwd_qid, query_sum)

    def add_reverse_result_summary(self, fwd_qobj, fwd_uobj, rev_uobj, fwd_db,
            query_sum, spec_qid):
        """Returns hits for reverse search"""
        if query_sum.check_db_summary(fwd_db):
            result_sum = query_sum.fetch_db_summary(fwd_db)
        else:
            result_sum = summary_obj.ResultSummary(fwd_db)
        if not (self.check_parsed_output(fwd_uobj)) or (self.check_parsed_output(rev_uobj)):
            pass # freak out
        fwd_hits = fwd_uobj.parsed_result.descriptions
        self.add_reverse_hits(fwd_qobj, fwd_hits, rev_uobj, result_sum, spec_qid)
        if not result_sum.determined():
            #print(result_sum.db)
            #print(result_sum.positive_hit_list)
            if len(result_sum.positive_hit_list) > 0:
                result_sum.determined('positive')
            elif len(result_sum.tentative_hit_list) > 0:
                result_sum.determined('tentative')
            elif len(result_sum.unlikely_hit_list) > 0:
                result_sum.determined('unlikely')
        query_sum.add_db_summary(fwd_db, result_sum)

    def add_reverse_hits(self, fwd_qobj, fwd_hit_list, rev_uobj, result_sum, spec_qid):
        """Returns hits for reverse search"""
        #print(fwd_qobj.identity)
        if not self.fwd_max_hits:
            fwd_max_hits = len(fwd_hit_list)
        else:
            fwd_max_hits = self.fwd_max_hits
        fwd_hit_index = 0
        for fwd_hit in fwd_hit_list:
            #new_title = search_util.remove_blast_header(fwd_hit.title)
            #print('forward hit is ' + new_title + ' ' + str(fwd_hit.e))
            if (fwd_hit_index == fwd_max_hits) or (fwd_hit.e > self.fwd_evalue):
                #print("stopping at forward hit scans")
                break # don't need to look further
            elif (self.fwd_evalue is None) or (fwd_hit.e < self.fwd_evalue):
                if rev_uobj.query in fwd_hit.title: # matching hit/reverse search pair
                    #print("matching reverse object for " + rev_uobj.name)
                    #print(fwd_hit.title)
                    rev_hits = rev_uobj.parsed_result.descriptions
                    status,pos_hit,neg_hit,e_diff = self.reverse_hit_status(
                            fwd_qobj, rev_hits, spec_qid)
                    #print(status)
                    #print(pos_hit)
                    #print(neg_hit)
                    fwd_id = search_util.remove_blast_header(fwd_hit.title)
                    if status != 'negative': # there is a hit to add
                        #print('hit status ' + status)
                        hit = summary_obj.Hit(fwd_id, fwd_hit.e,
                            search_util.remove_blast_header(pos_hit.title), pos_hit.e,
                            search_util.remove_blast_header(neg_hit.title), neg_hit.e,
                            e_diff, status)
                        #for k,v in hit.__dict__.items():
                            #print(str(k) + ' ' + str(v))
                        result_sum.add_hit(fwd_id, hit, status)
            fwd_hit_index += 1

    def reverse_hit_status(self, fwd_qobj, rev_hit_list, spec_qid):
        """Determines the status of a forward hit based on reverse search"""
        status = 'negative'
        first_positive_hit = None
        first_negative_hit = None
        e_diff = None
        if not self.rev_max_hits:
            rev_max_hits = len(rev_hit_list)
        else:
            rev_max_hits = self.rev_max_hits
        rev_hit_index = 0
        for rev_hit in rev_hit_list:
            #print(rev_hit.title + ' ' + str(rev_hit.e))
            if (rev_hit_index == rev_max_hits) or (rev_hit.e > self.rev_evalue):
                #print('stopping reverse scan')
                break # both of these conditions means we don't need to look more
            if rev_hit.e == 0:
                #print("zero value evalue")
                rev_hit.e = 1e-179 # this is purportedly the threshold at which E-values default to 0
            if (self.rev_evalue is None) or (rev_hit.e < self.rev_evalue):
                new_title = search_util.remove_blast_header(rev_hit.title).split(' ',1)[0]
                match = False
                if fwd_qobj.search_type == 'seq':
                    if (new_title == fwd_qobj.identity) or\
                        (self.check_raccs(new_title,fwd_qobj.raccs)):
                        match = True
                elif fwd_qobj.search_type == 'hmm':
                    assoc_qobj = self.mqdb[spec_qid] # use spec_qid from result; not qobj
                    if (new_title == spec_qid) or\
                        (self.check_raccs(new_title,assoc_qobj.raccs)):
                        match = True
                if match:
                    #print("match")
                    if first_negative_hit: # this is the first positive hit
                        #print('checking an unlikely hit')
                        #print(first_negative_hit.e)
                        #print(rev_hit.e)
                        #print(math.fabs(math.log(first_negative_hit.e,10) - math.log(rev_hit.e,10)))
                        # Here we want the difference to be less, i.e. the separation is not convincing
                        e_diff = math.fabs(math.log(first_negative_hit.e,10) - math.log(rev_hit.e,10))
                        if (self.next_evalue is None) or e_diff < self.next_evalue:
                            #print('hit is unlikely')
                            status = 'unlikely'
                            first_positive_hit = rev_hit
                        else:
                            #print('hit is negative')
                            status = 'negative'
                        #print()
                        break
                    if rev_hit_index == (len(rev_hit_list)-1):
                        status = 'positive'
                        break # we only found positive hits
                    if rev_hit_index == 0:
                        #print('first hit is positive')
                        first_positive_hit = rev_hit # store a ref to the first positive hit
                else: # not a match
                    if not first_negative_hit:
                        #print('found first negative hit')
                        first_negative_hit = rev_hit # store a ref to the first negative hit
                    if first_positive_hit: # this is the first non-match hit
                        #print('checking a likely hit')
                        #print(first_positive_hit.e)
                        #print(rev_hit.e)
                        #print(math.fabs(math.log(first_positive_hit.e,10) - math.log(rev_hit.e,10)))
                        # Here we want the difference to be greater, i.e. the separation is convincing
                        e_diff = math.fabs(math.log(first_positive_hit.e,10) - math.log(rev_hit.e,10))
                        if (self.next_evalue is None) or e_diff > self.next_evalue:
                            #print('hit is positive')
                            status = 'positive'
                        else:
                            #print('hit is tentative')
                            status = 'tentative'
                        #print()
                        break # status determined
            #print()
            rev_hit_index += 1
        #print()
        #print(status)
        #print(first_positive_hit)
        return (status, first_positive_hit, first_negative_hit, e_diff)

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

    def check_raccs(self, acc, racc_list):
        """Returns true if accession in list of redundant accessions"""
        for racc,evalue in racc_list:
            if acc in racc:
                return True
        return False

###########################################
# Code for summarizing multiple summaries #
###########################################

class SummSummarizer:
    def __init__(self, summ_obj, summ_list):
        self.mobj = summ_obj # actual summary object
        self.summ_list = summ_list # list of other summary objects to summarize
        self.qdb = configs['query_db']
        self.sdb = configs['search_db']
        self.udb = configs['result_db']
        self.mdb = configs['summary_db']
        self.sqdb = configs['search_queries']
        self.mqdb = configs['misc_queries']

    def add_summaries(self):
        """For each summary in the summ_list, add the results"""
        print('adding summaries')
        for summ_id in self.summ_list:
            self.add_summary(summ_id)
        print('updating statuses')
        self.update_statuses()

    def add_summary(self, summ_id):
        """
        Fetches the relevant summary object from the summary database based on
        'summ_id'; traverses the object and populates the new summary_obj.
        """
        to_add = self.mdb[summ_id]
        for qid in to_add.query_list:
            ta_qobj = to_add.queries[qid]
            ta_qid = self.filter_qid(qid, to_add)
            qobj = self.get_qobj(ta_qid, self.mobj)
            for db in ta_qobj.db_list:
                ta_dbobj = ta_qobj.dbs[db]
                db_obj = self.get_dbobj(db, qobj)
                for hit_list in ta_dbobj.lists:
                    hlist = getattr(ta_dbobj,hit_list)
                    for hit_id in hlist:
                        hobj = db_obj.get_hit(hit_id)
                        if hit_list == 'positive_hit_list':
                            hobj.add_summary(summ_id)
                        elif hit_list == 'tentative_hit_list':
                            hobj.add_summary(summ_id, 'tentative')
                        else:
                            hobj.add_summary(summ_id, 'unlikely')

    def update_statuses(self):
        """Called after all summaries added; determines status of all hits/dbs"""
        for qid in self.mobj.query_list:
            qobj = self.mobj.queries[qid]
            for db in qobj.db_list:
                db_obj = qobj.dbs[db]
                for hit_id in db_obj.hit_list:
                    hobj = db_obj.hits[hit_id]
                    hobj.determine_status()
                db_obj.determine_status()

    def filter_qid(self, qid, mobj):
        """Filters a qid to return spec_qid if hmmer search"""
        if mobj.fwd_algorithm == 'hmmer':
            qobj = self.qdb[qid]
            return qobj.spec_qid
        return qid

    def get_qobj(self, qid, mobj):
        """Returns qobj if exists, else makes one"""
        if mobj.check_query_summary(qid):
            return mobj.queries[qid]
        else:
            qobj = summary_obj.QuerySummary(qid)
            mobj.add_query_summary(qid, qobj)
            return qobj

    def get_dbobj(self, db, qobj):
        """Returns dbobj if exists, else makes one"""
        if qobj.check_db_summary(db):
            return qobj.dbs[db]
        else:
            db_obj = summary_obj.ResultfromSummaries(db)
            qobj.add_db_summary(db, db_obj)
            return db_obj
