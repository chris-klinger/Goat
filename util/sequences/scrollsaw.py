"""
This module contains code to implement scrollsaw in Goat. Scrollsaw requires a
summary to work off of, a selection criteria (usually supergroup), and a number
of sequences from each supergroup to select for minimum genetic distance.

The main ScrollSaw object takes care of gathering the summary and getting the
necessary sequences using 'seqs_from_summary' - importantly, the relevant files
are captured in a dict for each query in the summary to ensure flawless matching
of sequence files to queries/groups. Each query is then used to create another
object, which itself takes care of actually running the scrollsaw protocol
(comparing all files for distance between sequences, gathering accessions up
to the number required, and then writing these sequences out as their own
specific scrollsaw file).
"""

import os
from itertools import combinations

from Bio import SeqIO

from util import util
from util.sequences import seqs_from_summary
from util.alignment import mafft
from phylo import raxml

# Eventually go through settings
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class SummaryScrollSaw:
    def __init__(self, basename, summary_obj, target_dir, sort_group, num_seqs):
        self.bname = basename
        self.mobj = summary_obj
        self.target_dir = target_dir
        self.sgroup = sort_group
        self.num_seqs = num_seqs
        self.gdict = None # populated during run

    def run(self):
        """
        Calls get_sequences() first to populate seq_files, then creates new
        ScrollSaw objects for each set of query files.
        """
        self.get_sequences()
        for qid in self.mobj.query_list:
            qgroup_dict = {}
            for sg,sg_file in self.gdict[qid]:
                qgroup_dict[sg_file] = sg
            q_scrollsaw = QueryScrollSaw(qid, qgroup_dict, self.target_dir,
                    self.num_seqs)
            q_scrollsaw.run()

    def get_sequences(self):
        """Calls seqs_from_summary with appropriate params"""
        writer = seqs_from_summary.SummarySeqWriter(self.bname, self.mobj,
                self.target_dir, 'positive', '', self.sgroup)
        writer.run()
        self.gdict = writer.sg_dict

class QueryScrollSaw:
    def __init__(self, query, qgroup_dict, target_dir, num_seqs):
        self.qid = query
        self.gdict = qgroup_dict
        self.target_dir = target_dir
        self.num_seqs = int(num_seqs)
        self.num_start_files = self.calc_num_start_files()
        self.dist_dict = {} # dictionary to track distances for each sequence
        self.file_dict = {} # dictinary to compare seq_id to file_path
        self.id_dict = {} # dictionary to compare seq_id to simplified id
        self.rev_id_dict = {} # determines whether old headers already have unique headers
        self.counter = util.IDCounter() # for creating unique, short, IDs
        self.files = [] # keep track of all files and delete them at the end

    def calc_num_start_files(self):
        """Utility function"""
        return int(len(self.gdict.keys()))

    def run(self):
        sg_files = list(self.gdict.keys())
        for f1,f2 in combinations(sg_files,2): # all files
            sg1 = self.gdict[f1]
            sg2 = self.gdict[f2]
            # Combine files into new file
            new_seq_file = self.cat_and_dist(f1,f2,sg1,sg2)
            self.files.append(new_seq_file)
            # Align file
            msa_file = new_seq_file.rsplit('.',1)[0] + '.mfa'
            self.files.append(msa_file)
            mafft.MAFFT(new_seq_file,msa_file).run_from_file()
            # Run RAxML to get distances
            dist_base = (os.path.basename(msa_file)).rsplit('.',1)[0] # without extension
            raxml.RAxML(msa_file, dist_base, tmp_dir).get_distances()
            dist_file = os.path.join(tmp_dir,
                    ('RAxML_distances.' + dist_base))
            self.files.append(dist_file)
            # Add distances to dict
            self.add_distances_to_dict(dist_file)
        self.write_outfiles()
        for tmp_file in self.files:
            os.remove(tmp_file)

    def cat_and_dist(self, f1, f2, sg1, sg2):
        """Cats two files and populates dist_dict with simplified headers"""
        basename = str(self.qid) + sg1 + sg2 + '.fa'
        outpath = os.path.join(tmp_dir, basename) # gets a unique filename
        with open(outpath,'w') as o:
            for infile in (f1,f2):
                with open(infile,'U') as i:
                    for line in i:
                        if line.startswith('>'):
                            header = line.strip('\n').lstrip('>')
                            if header in self.rev_id_dict.keys():
                                new_header = self.rev_id_dict[header]
                            else:
                                new_header = self.get_new_id(header)
                                self.rev_id_dict[header] = new_header
                            self.id_dict[new_header] = header # compare to old header
                            self.file_dict[header] = infile # keep track of where the header came from
                            # write shorter header to new file
                            o.write('>' + new_header + '\n')
                        else:
                            line = line.replace('.','-')
                            o.write(line) # re-write to outfile
        return outpath

    def get_new_id(self, old_id):
        """Gets a new simplified id without spaces"""
        id_num = self.counter.get_new_id()
        return ('seq' + str(id_num))

    def add_distances_to_dict(self, dfile):
        """Adds values from file to internal dictionary"""
        with open(dfile,'U') as d:
            for line in d:
                l = line.strip('\n')
                llist = l.split()
                acc1 = llist[0]
                acc2 = llist[1]
                dist = float(llist[2]) # need float to sum properly

                for acc in (acc1,acc2):
                    try:
                        self.dist_dict[acc].append(dist)
                    except(KeyError):
                        self.dist_dict[acc] = []
                        self.dist_dict[acc].append(dist)

    def write_outfiles(self):
        """Writes reduced files to target_dir"""
        outname = str(self.qid) + '_scrollsaw.fa'
        outpath = os.path.join(self.target_dir,outname)
        added = {} # to keep track of number added for each sg
        for sg in self.gdict.values():
            added[sg] = 0
        to_write = {}
        num_added = 0
        total_needed = self.num_seqs * self.num_start_files # might not always reach this
        for k,v in sorted(self.dist_dict.items(), key=lambda x: sum(x[1])):
            #print(k)
            #print(sum(v))
            if num_added == total_needed: # we have enough
                break
            (old_acc,acc_file,sg) = self.get_info_from_new_header(k)
            #print(old_acc)
            #print(acc_file)
            #print(sg)
            if added[sg] == self.num_seqs: # found enough already for this group
                #print("stopping adding for {}".format(sg))
                pass
            else:
                try:
                    to_write[acc_file].append(old_acc)
                except(KeyError):
                    to_write[acc_file] = []
                    to_write[acc_file].append(old_acc)
                finally:
                    #print("incrementing values")
                    added[sg] += 1
                    num_added += 1
        with open(outpath,'w') as o:
            for acc_file in to_write.keys():
                seq_records = SeqIO.parse(acc_file,'fasta')
                for record in seq_records:
                    if str(record.description) in to_write[acc_file]:
                        SeqIO.write(record, o, 'fasta')

    def get_info_from_new_header(self, acc):
        """Traverses myriad of dicts to return sg associated with a new acc"""
        old_acc = self.id_dict[acc]
        acc_file = self.file_dict[old_acc]
        sg = self.gdict[acc_file]
        return (old_acc,acc_file,sg)
