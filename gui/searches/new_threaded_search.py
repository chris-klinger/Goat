"""
This module contains updated code for providing user updates on searches in Goat.
Not sure if this will work properly without threading, but will try; either way,
trying to separate user information for searches from the search itself, and
provide a better way to feed back the callback from a search to the main GUI
regardless of whether or not threading is used.
"""

import threading, queue, os

from tkinter import *
from tkinter import ttk

from bin.initialize_goat import configs

from searches import new_search_runner, search_obj
from searches.hmmer import hmmer_build
from results import intermediate
from summaries import summary_obj, summarizer
from util.sequences import seqs_from_summary
from util.alignment import mafft
from queries import query_file

blast_path = '/usr/local/ncbi/blast/bin'
hmmer_path = '/Users/cklinger/src/hmmer-3.1b1-macosx-intel/src'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class ProgressFrame(Frame):
    def __init__(self, starting_sobj, mode, parent=None, threaded=True,
            other_widget=None, callback=None, callback_args=None,
            rev_search_name=None, keep_rev_output=None, **kwargs):
        Frame.__init__(self, parent)
        self.pack(expand=YES, fill=BOTH)
        self.start_sobj = starting_sobj
        self.mode = mode
        self.threaded = threaded
        self.other = other_widget
        self.callback = callback
        self.callback_args = callback_args
        # Some attributes are only applicable for analyses
        self.rev_name = rev_search_name
        self.rev_ko = keep_rev_output
        if kwargs:
            self.kwargs = {}
            for k,v in kwargs.items():
                self.kwargs[k] = v # store for later access
        # Some search modes require access to dbs
        self.qdb = configs['query_db']
        self.udb = configs['result_db']
        self.sdb = configs['search_db']

        # Make non-modal, i.e. un-closeable
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', lambda: None)

        # Add some information, keep a ref to change the text later
        self.search_info = Label(self, text='Searching databases using {}'.format(
            self.start_sobj.algorithm), anchor='center', justify='center')
        self.search_info.pack(expand=YES)

        # Determine the maximum number of searches to do
        self.num_todo = self.determine_max_searches(self.start_sobj, mode)
        # Code to add progress bar, update 'value' attr after each search
        self.p = ttk.Progressbar(self, # parent
                orient = HORIZONTAL,
                length = 200,
                mode = 'determinate', # specifies a set number of steps
                maximum = self.num_todo)
        self.p.pack()
        # Default starting value for the search bar
        self.num_finished = 1 # don't index from zero, first search is number 1

        # Add another label to report hard numbers in progress bar
        self.search_label = Label(self, text='Performing search {} of {}'.format(
            self.num_finished, self.num_todo), anchor='center', justify='center')
        self.search_label.pack(side=BOTTOM, expand=YES)

    def run(self):
        """start producer thread, consumer loop"""
        if self.threaded:
            configs['threads'].add_thread()
            # always create the queue
            self.queue = queue.Queue()
            if self.mode == 'racc':
                threading.Thread(target=self._run_racc_blast).start()
            elif self.mode == 'new':
                threading.Thread(target=self._run_fwd_search).start()
            elif self.mode == 'rev':
                threading.Thread(target=self._run_rev_search).start()
            elif self.mode == 'recip_blast':
                threading.Thread(target=self._run_recip_blast).start()
            elif self.mode == 'hmmer_blast':
                threading.Thread(target=self._run_hmmer_blast).start()
            elif self.mode == 'full_blast_hmmer':
                threading.Thread(target=self._run_full_blast_hmmer).start()
            # always start the thread consumer function
            self.thread_consumer()
        else:
            pass

    def thread_consumer(self):
        """Checks the queue regularly for new results"""
        # Even if there are no results to grab, update status bar each time
        self.p['value'] = self.num_finished
        self.search_label['text'] = 'Performing search {} of {}'.format(
            self.num_finished, self.num_todo)
        try:
            done = self.queue.get(block=False)
        except(queue.Empty): # nothing to grab
            self.after(200, self.thread_consumer)
        # when finished
        else:
            if done:
                if self.callback:
                    if self.callback_args:
                        self.callback(*self.callback_args)
                    else:
                        self.callback()
            self.parent.destroy()

    def increment_search_count(self):
        """Increments counter after each search finishes"""
        #print("incrementing counter")
        if self.num_finished == self.num_todo:
            pass # don't increment past max
        else:
            self.num_finished += 1

    def determine_max_searches(self, sobj, mode):
        """Determines the number of searches to run"""
        if mode == 'racc' or mode == 'rev':
            return len(sobj.queries)
        elif mode == 'new' or mode == 'recip_blast':
            return (len(sobj.queries) * len(sobj.databases))

####################################
# Actual code for running searches #
####################################

    def _run_racc_blast(self):
        """Runs blast searches for raccs, and then removes all info after"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='racc',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done') # signal completion

    def _run_fwd_search(self):
        """Function called by the thread, runs each BLAST search"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='new',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def _run_rev_search(self):
        """Calls Search Runner for reverse searches"""
        runner = new_search_runner.SearchRunner(self.start_sobj, mode='rev',
                other_widget=self)
        runner.run()
        runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def _run_recip_blast(self):
        """
        Populates and runs a SearchRunner object for the forward BLAST, then obtains
        queries and a new sobj for the reverse search. Refreshes label and counter,
        then runs the SearchRunner object for the reverse BLAST. Commits all changes
        at the end. - Can we update the db from a thread?
        """
        # Run the forward search, parse output
        fwd_runner = new_search_runner.SearchRunner(self.start_sobj, mode='new',
                other_widget=self)
        fwd_runner.run()
        fwd_runner.parse()
        # Populate DBs with intermediate search queries
        intermediate.Search2Queries(self.start_sobj).populate_search_queries()
        # Get the relvant qids
        rev_queries = []
        for uid in self.start_sobj.list_results():
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                rev_queries.append(qid)
        rev_sobj = search_obj.Search(
                name = self.rev_name,
                algorithm = 'blast',
                q_type = self.start_sobj.db_type,
                db_type = self.start_sobj.q_type,
                queries = rev_queries,
                databases = [], # rev search
                keep_output = self.rev_ko,
                output_location = self.start_sobj.output_location)
        self.sdb.add_entry(rev_sobj.name, rev_sobj)
        # Reset label and counter
        self.search_info['text'] = 'Performing reverse search using blast'
        self.num_todo = self.determine_max_searches(rev_sobj, 'rev')
        self.p['maximum'] = self.num_todo
        self.num_finished = 1
        fwd_runner = new_search_runner.SearchRunner(rev_sobj, mode='rev',
                other_widget=self)
        fwd_runner.run()
        fwd_runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def _run_hmmer_blast(self):
        """
        Populates and runs a SearchRunner object for the forward HMMer, then obtains
        queries and a new sobj for the reverse search. Refreshes label and counter,
        then runs the SearchRunner object for the reverse BLAST. Commits all changes
        at the end. - Can we update the db from a thread?
        """
        # Run the forward search, parse output
        fwd_runner = new_search_runner.SearchRunner(self.start_sobj, mode='new',
                other_widget=self)
        fwd_runner.run()
        fwd_runner.parse()
        # Populate DBs with intermediate search queries
        intermediate.Search2Queries(self.start_sobj).populate_search_queries()
        # Get the relvant qids
        rev_queries = []
        for uid in self.start_sobj.list_results():
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                rev_queries.append(qid)
        rev_sobj = search_obj.Search(
                name = self.rev_name,
                algorithm = 'blast',
                q_type = self.start_sobj.db_type,
                db_type = self.start_sobj.q_type,
                queries = rev_queries,
                databases = [], # rev search
                keep_output = self.rev_ko,
                output_location = self.start_sobj.output_location)
        self.sdb.add_entry(rev_sobj.name, rev_sobj)
        # Reset label and counter
        self.search_info['text'] = 'Performing reverse search using blast'
        self.num_todo = self.determine_max_searches(rev_sobj, 'rev')
        self.p['maximum'] = self.num_todo
        self.num_finished = 1
        rev_runner = new_search_runner.SearchRunner(rev_sobj, mode='rev',
                other_widget=self)
        rev_runner.run()
        rev_runner.parse()
        if self.threaded:
            self.queue.put('Done')

    def _run_full_blast_hmmer(self):
        """
        Populates and runs a SearchRunner object for the forward BLAST, runs a
        subsequent reverse BLAST, summarizes based on user input and then uses
        all "positive" hits to build a new MSA and subsequent HMM before running
        another forward HMMer/reverse BLAST combo.
        """
        # Run the forward search, parse output
        fwd_runner = new_search_runner.SearchRunner(self.start_sobj, mode='new',
                other_widget=self)
        fwd_runner.run()
        fwd_runner.parse()
        # Populate DBs with intermediate search queries
        intermediate.Search2Queries(self.start_sobj).populate_search_queries()
        # Get the relvant qids
        rev_queries = []
        for uid in self.start_sobj.list_results():
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                rev_queries.append(qid)
        rev_sobj = search_obj.Search(
                name = self.rev_name,
                algorithm = 'blast',
                q_type = self.start_sobj.db_type,
                db_type = self.start_sobj.q_type,
                queries = rev_queries,
                databases = [], # rev search
                keep_output = self.rev_ko,
                output_location = self.start_sobj.output_location)
        self.sdb.add_entry(rev_sobj.name, rev_sobj)
        # Reset label and counter
        self.search_info['text'] = 'Performing reverse search using blast'
        self.num_todo = self.determine_max_searches(rev_sobj, 'rev')
        self.p['maximum'] = self.num_todo
        self.num_finished = 1
        # Run reverse search, parse output
        rev_runner = new_search_runner.SearchRunner(rev_sobj, mode='rev',
                other_widget=self)
        rev_runner.run()
        rev_runner.parse()
        # Summarize fwd and rev search using cutoff criteria
        int_summary = summary_obj.Summary(
            fwd_search = self.start_sobj.name,
            fwd_qtype = self.start_sobj.q_type,
            fwd_dbtype = self.start_sobj.db_type,
            fwd_algorithm = self.start_sobj.algorithm,
            fwd_evalue_cutoff = self.kwargs['fwd_evalue'],
            fwd_max_hits = self.kwargs['fwd_hits'],
            rev_search = self.rev_name,
            rev_qtype = self.start_sobj.db_type,
            rev_dbtype = self.start_sobj.q_type,
            rev_algorithm = 'blast',
            rev_evalue_cutoff = self.kwargs['rev_evalue'],
            rev_max_hits = self.kwargs['rev_hits'],
            next_hit_evalue_cutoff = self.kwargs['next_evalue'])
        int_summarizer = summarizer.SearchSummarizer(int_summary)
        int_summarizer.summarize_two_results()
        mdb = configs['summary_db']
        mdb.add_entry(self.kwargs['summ_name'], int_summary) # should we make it nameable?
        # Get sequences from summarized results - positive only!
        seq_writer = seqs_from_summary.SummarySeqWriter(
                basename = self.start_sobj.name,
                summary_obj = int_summary,
                target_dir = self.start_sobj.output_location,
                hit_type = 'positive',
                mode = 'all',
                add_query_to_file = True) # last one adds the query object seq as well
        seq_writer.run()
        # Now create MSAs and HMMs for all files
        msa_dict = {}
        for qid,filename in seq_writer.file_dict.items():
            msa_file = (filename.rsplit('.',1)[0]) + '.mfa'
            msa_dict[qid] = msa_file
            mafft.MAFFT(filename,msa_file).run('file')
        hmm_dict = {}
        for qid,msafile in msa_dict.items():
            hmm_file = (msafile.rsplit('.',1)[0]) + '.hmm'
            hmm_dict[qid] = hmm_file
            hmmer_build.HMMBuild(
                    hmmbuild_path = hmmer_path,
                    msa_filepath = msafile,
                    hmm_out = hmm_file).run_from_file()
        # Create new intermediate queries for forward HMMer search and run
        qdb = configs['query_db']
        hmmer_queries = []
        for qid,hmmfile in hmm_dict.items():
            name,hmm_obj = query_file.HMMFile(
                    hmmfile,self.start_sobj.db_type).get_query()
            hmm_obj.spec_qid = qid
            qobj = qdb[qid]
            hmm_obj.spec_record = qobj.record
            hmm_obj.add_query(qid,qobj) # copy from qdb to misc_qdb
            qdb[name] = hmm_obj # add to db
            hmmer_queries.append(name) # add to queries to search
        fwd_hmmer = search_obj.Search( # be explicit for clarity here
            name = self.kwargs['fwd_name'],
            algorithm = 'hmmer',
            q_type = self.start_sobj.q_type, # queries come from original DB/query type
            db_type = self.start_sobj.db_type, # target DB type is same as original db type
            queries = hmmer_queries, # fresh batch of queries for new fwd search
            databases = self.start_sobj.databases, # searching in all dbs again
            keep_output = self.kwargs['fwd_ko'], # specified for new search
            output_location = self.start_sobj.output_location)
        self.sdb.add_entry(fwd_hmmer.name, fwd_hmmer)
        # Reset label and counter again
        self.search_info['text'] = 'Performing forward search using hmmer'
        self.num_todo = self.determine_max_searches(fwd_hmmer, 'new')
        self.p['maximum'] = self.num_todo
        self.num_finished = 1
        # Run the forward search, parse output
        new_fwd_runner = new_search_runner.SearchRunner(fwd_hmmer, mode='new',
                other_widget=self)
        new_fwd_runner.run()
        new_fwd_runner.parse()
        # Again, get new queries from fwd hmmer search
        #print()
        #print("Getting rev2 search queries")
        intermediate.Search2Queries(fwd_hmmer).populate_search_queries()
        # Get the relvant qids
        rev_blast_queries = []
        for uid in fwd_hmmer.list_results():
            uobj = self.udb[uid]
            for qid in uobj.list_queries():
                rev_blast_queries.append(qid)
        #print(rev_blast_queries)
        rev_blast_sobj = search_obj.Search(
                name = self.kwargs['rev_name'],
                algorithm = 'blast',
                q_type = fwd_hmmer.db_type,
                db_type = fwd_hmmer.q_type,
                queries = rev_blast_queries,
                databases = [], # rev search
                keep_output = self.kwargs['rev_ko'],
                output_location = self.start_sobj.output_location)
        self.sdb.add_entry(rev_blast_sobj.name, rev_blast_sobj)
        # Reset label and counter
        #print("Performing rev2 blast search")
        self.search_info['text'] = 'Performing reverse search using blast'
        self.num_todo = self.determine_max_searches(rev_blast_sobj, 'rev')
        self.p['maximum'] = self.num_todo
        self.num_finished = 1
        rev_runner = new_search_runner.SearchRunner(rev_blast_sobj, mode='rev',
                other_widget=self)
        rev_runner.run()
        rev_runner.parse()
        # Finally, signal completion for callback DB commits
        if self.threaded:
            self.queue.put('Done')

