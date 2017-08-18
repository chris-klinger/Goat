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

import os

from Bio import SeqIO

from bin.initialize_goat import configs

class SummarySeqWriter:
    def __init__(self, basename, summary_obj, target_dir, hit_type,
            mode, extra_groups=None):
        self.bname = str(basename)
        self.mobj = summary_obj
        self.target_dir = target_dir
        self.htype = hit_type
        self.mode = mode
        self.extra = extra_groups
        # dbs are global objects
        self.rdb = configs['record_db']
        # internal data structure to track record objects
        self.hdict = {}

    def run(self):
        """Calls all internal functions"""
        #print('calling run')
        self.collect_ids()
        self.write_to_output()

    def parse(self, filepath):
        """Parses a target file"""
        #print('calling parse')
        return SeqIO.parse(filepath, "fasta")

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
            self.collect_dbs(query)

    def collect_dbs(self, query):
        """Called per query to run a call for each db"""
        #print('calling collect_dbs')
        qobj = self.mobj.queries[query]
        for db in qobj.db_list:
            #print(db)
            self.collect_hit_ids(query, qobj, db)

    def collect_hit_ids(self, query, qobj, db):
        """Collects the actual ids for each database"""
        #print('calling collect_hit_ids')
        #print(query)
        #print(qobj)
        #print(db)
        db_obj = qobj.dbs[db]
        for hlist_name in db_obj.lists:
            hlist = getattr(db_obj,hlist_name)
            if len(hlist) > 0: # there are hits
                hits = []
                hits.append(query) # add the query id
                hit_type = hlist_name.split('_')[0] # positive, tentative, or unlikely
                #print(hit_type)
                hits.append(hit_type) # add title
                for rid in hlist:
                    #print(rid)
                    hits.append(rid)
                if not db in self.hdict.keys():
                    self.hdict[db] = []
                self.hdict[db].append(hits) # makes a list of lists
                #print(self.hdict)

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
            robj = self.rdb[rid]
            for k,v in robj.files.items():
                if v.filetype == ftype:
                    target_file = v.filepath
            seq_records = self.parse(target_file)
            for hit_list in self.hdict[rid]:
                query = hit_list[0]
                hit_type = hit_list[1]
                hits = hit_list[2:]
                #print(hits)
                if hit_type in self.htype: # we want these hits written
                    target_files = []
                    if 'all' in self.mode:
                        all_file = self.get_output_file([query, 'all', hit_type])
                        target_files.append(all_file)
                    if 'db' in self.mode:
                        db_file = self.get_output_file([query, rid, hit_type])
                        target_files.append(db_file)
                    # could continue for arbitrary number of sets...
                    # get all the records to write just once
                    to_write = []
                    for record in seq_records:
                        if str(record.description) in hits:
                            to_write.append(record)
                    # finally, write all records to all desired files
                    for tfile in target_files:
                        if os.path.exists(tfile):
                            o = open(tfile,'a')
                        else:
                            o = open(tfile,'w')
                        try:
                            for record in to_write:
                                SeqIO.write(record, o, "fasta")
                        finally:
                            o.close() # always close file

