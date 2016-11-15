"""
This module contains classes to model various kinds of BLAST searches that
can be carried out through the Goat interface. Each different search is a
subclass of the BLAST superclass, which defines methods and attributes
common to all such searches.
"""

import os, subprocess

class BLAST():
    """
    Parental BLAST class from which all BLAST subclasses derive. Allows
    changing the basic parameters common to all BLAST searches. Parameters
    specific to one or more flavours of BLAST are instead taken care of
    by the specific subclass(es).
    """
    valid_options = ['query_loc', 'evalue', 'subject', 'subject_loc',
        'show_gis', 'num_descriptions', 'num_alignments', 'max_target_seqs',
        'max_hsps', 'html', 'gilist', 'negative_gilist', 'entrez_query',
        'culling_limit', 'best_hit_overhang', 'best_hit_score_edge',
        'dbsize', 'searchhsp', 'import_search_strategy', 'export_search_strategy',
        'parse_deflines', 'num_threads', 'remote', 'outfmt']

    def __init__(self, blast_path, query, db, out, **kwargs):
        self.blast_path = blast_path
        self.query = query
        self.db = db
        self.out = out
        self.kwargs = kwargs

    def run(self, blast_type, valid_options=valid_options):
        """Runs the actual BLAST search"""
        print(self.blast_path)
        args = []
        # first argument should always be the type of BLAST
        args.append(os.path.join(self.blast_path, blast_type))
        for k,v in self.__dict__.items():
            if not str(k) in ['blast_path','kwargs']: # ignore these
                args.append('-' + str(k))
                args.append(str(v))
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options: # will the program understand it?
                    args.append('-' + str(k))
                    args.append(str(v))
        #print(args)
        try:
            subprocess.run(args)
        except(Exception):
            print("Could not run BLAST for {} in {}".format(
                self.query, self.db))

class BLASTn(BLAST):
    """Subclass for BLASTn searches"""
    blastn_options = ['word_size', 'gapopen', 'gapextend', 'reward',
        'penalty', 'strand', 'dust', 'filtering_db', 'window_masker_taxid',
        'window_masker_db', 'soft_masking', 'lcase_masking', 'db_soft_mask',
        'db_hard_mask', 'perc_identity', 'template_type', 'template_length',
        'use_index', 'index_name', 'xdrop_ungap', 'xdrop_gap',
        'xdrop_final_gap', 'no_greedy', 'min_raw_gapped_score', 'ungapped',
        'window_size']
    valid_options = BLAST.valid_options.extend(blastn_options)

    def run(self, valid_options):
        BLAST.run("blastn", valid_options)

class BLASTp(BLAST):
    """Subclass for BLASTp searches"""
    blastp_options = ['word_size', 'gapopen', 'gapextend', 'matrix',
        'threshold', 'comp_based_stats', 'seg', 'soft_masking',
        'lcase_masking', 'db_soft_mask', 'db_hard_mask',
        'xdrop_gap_final', 'window_size', 'use_sw_tback']
    valid_options = BLAST.valid_options.extend(blastp_options)

    def run(self, valid_options=valid_options):
        BLAST.run(self, "blastp", valid_options)
