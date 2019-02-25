"""
This module contains code for getting sequences from summary objects in the DB.
Retrieved sequences have several possible uses:
    -Re-alignment and creation of HMMer objects
    -Downstream phylogenetics
    -Domain prediction
    -Scrollsaw
Therefore, it would be nice to be able to be able to control how sequences are
ouput (e.g. group all sequences of each class together, group sequences of
each class by some shared feature (e.g. record, supergroup, strain, etc).

Idea here is to allow specifying different modes, and then to go through all
of the associated hits in the summary object, grab the sequences for each one,
and then, based on the specified mode(s), write the sequences to relevant
file(s).
"""

import os,re

from Bio import SeqIO

from bin.initialize_goat import configs

from util import util

class SummarySeqWriter:
    def __init__(self, basename, summary_obj, target_dir, hit_type,
            mode, extra_groups=None, add_query_to_file=False):
        self.bname = str(basename)
        self.mobj = summary_obj
        self.target_dir = target_dir
        self.htype = hit_type
        self.mode = mode
        self.extras = extra_groups
        self.add_query = add_query_to_file
        # dbs are global objects
        self.rdb = configs['record_db']
        # internal data structure to track record objects
        self.hdict = {}
        # internal data structure for file names; used in some contexts
        self.file_dict = {}
        # internal data structure to keep track of file names for SGs (ScrollSaw)
        self.sg_dict = {}
        # internal list to prevent all duplicates
        self.all_hits = []

    def run(self):
        """Calls all internal functions"""
        #print('calling run')
        self.collect_ids()
        self.write_to_output()

    def parse(self, filepath):
        """Parses a target file"""
        #print('calling parse')
        # return list else can only go through records once
        return list(SeqIO.parse(filepath, "fasta"))

    def get_output_file(self, args):
        """Function to return pathnames based on target_dir"""
        #print('calling get_output_file')
        out_name = self.bname
        for arg in args:
            out_name = out_name + '_' + str(arg)
        out_name = out_name + '.fa'
        return os.path.join(self.target_dir,out_name)

    def collect_ids(self):
        """Run for each query in summary"""
        #print('calling collect_ids')
        for query in self.mobj.query_list:
            #print(query)
            self.collect_dbs(query)
            #print()

    def collect_dbs(self, query):
        """Called per query to run a call for each db"""
        #print('calling collect_dbs')
        qobj = self.mobj.queries[query]
        for db in qobj.db_list:
            #print(db)
            self.collect_hit_ids(query, qobj, db)

    def collect_hit_ids(self, query, qobj, db):
        """Collects the actual ids for each database"""
        db_obj = qobj.dbs[db]
        if self.mobj.mode == 'result':
            #print('getting ids for result')
            for hlist_name in db_obj.lists:
                #print(hlist_name)
                hlist = getattr(db_obj,hlist_name)
                if len(hlist) > 0: # there are hits
                    #print(hlist_name)
                    hits = []
                    hits.append(query) # add the query id
                    hit_type = hlist_name.split('_')[0] # positive, tentative, or unlikely
                    #print(hit_type)
                    hits.append(hit_type) # add title
                    for qid in hlist:
                        #print(rid)
                        if not qid in self.all_hits: # Should prevent any duplicates across genomes?
                            hits.append(str(qid))
                            self.all_hits.append(qid)
                    if not db in self.hdict.keys():
                        self.hdict[db] = []
                    self.hdict[db].append(hits) # makes a list of lists
        elif self.mobj.mode == 'summary':
            if len(db_obj.hit_list) > 0:
                positive = [query, 'positive']
                tentative = [query, 'tentative']
                unlikely = [query, 'unlikely']
                for hit in db_obj.hit_list:
                    hit_obj = db_obj.hits[hit]
                    if hit_obj.status == 'positive':
                        if not hit in positive:
                            positive.append(hit)
                    elif hit_obj.status == 'tentative':
                        if not hit in tentative:
                            tentative.append(hit)
                    else:
                        if not hit in unlikely:
                            unlikely.append(hit)
                if not db in self.hdict.keys():
                    self.hdict[db] = []
                for hlist in [positive,tentative,unlikely]:
                    if len(hlist) > 2: # actually has hit ids
                        self.hdict[db].append(hlist) # makes a list of lists

    def write_to_output(self):
        """
        Main meat of the object, goes through the internal dict and uses
        information associated with each entry to write to one or more
        output files, which are either created or returned by the
        get_output_files() function.
        """
        #print('calling write_to_output')
        ftype = self.mobj.fwd_dbtype # type of file to look through
        for rid in self.hdict.keys():
            #print(rid)
            robj = self.rdb[rid]
            for k,v in robj.files.items():
                if v.filetype == ftype:
                    target_file = v.filepath
            seq_records = self.parse(target_file)
            for hit_list in self.hdict[rid]:
                query = hit_list[0]
                hit_type = hit_list[1]
                hits = hit_list[2:]
                #print(query)
                #`print(hits)
                if hit_type in self.htype: # we want these hits written
                    target_files = []
                    if 'all' in self.mode:
                        all_file = self.get_output_file([query, 'all', hit_type])
                        target_files.append(all_file)
                    if 'db' in self.mode:
                        db_file = self.get_output_file([query, rid, hit_type])
                        target_files.append(db_file)
                    if self.extras:
                        if 'supergroup' in self.extras:
                            sg_file = self.get_output_file([query,
                                robj.supergroup, hit_type])
                            if not query in self.sg_dict.keys(): # keep track for scrollsaw
                                self.sg_dict[query] = []
                            self.sg_dict[query].append([robj.supergroup, sg_file])
                            target_files.append(sg_file)
                    # could continue for arbitrary number of sets...
                    # get all the records to write just once
                    to_write = []
                    written = []
                    #seq_records = self.parse(target_file)
                    for record in seq_records:
                        if (record.description in hits or\
                            re.sub('\t','   ',record.description) in hits):
                            if not record.description in written:
                                to_write.append(record)
                                written.append(record.description) # ensures not written more than once
                    #print(to_write)
                    # finally, write all records to all desired files
                    for tfile in target_files:
                        if os.path.exists(tfile):
                            #print("opening existing file {}".format(tfile))
                            o = open(tfile,'a')
                        else:
                            #print("creating new file {}".format(tfile))
                            o = open(tfile,'w')
                            self.file_dict[query] = tfile # first time, add
                            if self.add_query:
                                self.write_query_seq(query,o)
                        try:
                            for record in to_write:
                                #SeqIO.write(record, o, "fasta")
                                self.write_result_seq(record,o)
                        finally:
                            o.close() # always close file
            #print()

    def write_query_seq(self, qid, outfile):
        """
        Write the query sequence associated with a given query ID to the output
        file as the first entry. Does not discriminate by hit_type (but could
        in the future?). Useful for intermediate alignments.
        """
        qdb = configs['query_db']
        qobj = qdb[qid]
        if qobj.search_type == 'seq':
            outfile.write('>' + str(qobj.description) + '\n')
            for chunk in util.split_input(str(qobj.sequence)):
                #print(chunk)
                outfile.write(chunk + '\n')
        elif qobj.search_type == 'hmm':
            pass # do we want to write for other query types?

    def write_result_seq(self, record, outfile):
        """Stand-in for now"""
        outfile.write('>' + str(record.description) + '\n')
        for chunk in util.split_input(str(record.seq)):
            outfile.write(chunk + '\n')
