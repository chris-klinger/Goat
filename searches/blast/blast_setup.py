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

    def __init__(self, blast_path, query, db, out, outfmt=5, **kwargs):
        self.blast_path = blast_path
        self.query = query
        self.db = db
        self.out = out
        self.outfmt = outfmt
        self.kwargs = kwargs

    def get_uniq_out(self, sep):
        """Gets a unique output file name"""
        db_name = os.path.basename(self.db)
        out_string = str(self.query.identity + sep + db_name + sep + 'out.txt')
        return os.path.join(self.out, out_string)

    def run_from_file(self, blast_type, valid_options=valid_options, sep='_'):
        """Runs BLAST using file as input"""
        args = []
        # first argument should always be the type of BLAST
        args.append(os.path.join(self.blast_path, blast_type))
        # note, query location here needs to be changed once a scheme is in place
        # to hold separate query files for each
        args.extend(['-query', self.query.location, '-db', self.db, '-out', self.out,
            '-outfmt', str(self.outfmt)])
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options: # will the program understand it?
                    args.append('-' + str(k))
                    args.append(str(v))
        try:
            subprocess.run(args)
        except(Exception):
            print("Could not run BLAST for {} in {}".format(
                self.query.identity, self.db))

    def run_from_stdin(self, blast_type, valid_options=valid_options, sep='_'):
        """Runs BLAST using obj as stdin"""
        args = []
        # first argument should always be the type of BLAST
        args.append(os.path.join(self.blast_path, blast_type))
        #out = self.get_uniq_out(sep='_')
        args.extend(['-db', self.db, '-out', self.out, '-outfmt', str(self.outfmt)])
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options:
                    args.append('-' + str(k))
                    args.append(str(v))
        try:
            # input is from stdin
            blast = subprocess.Popen(args, stdin=subprocess.PIPE)
            # description and sequence recapitulates the original FASTA format
            blast_query = '>' + str(self.query.description) + '\n' + str(self.query.sequence)
            blast.stdin.write(blast_query.encode('utf-8')) # note the encoding
            blast.communicate() # actually runs the search
            print('BLASTing from stdin')
        except(Exception):
            print("Could not run BLAST for {} in {}".format(
                self.query.identity, self.db))

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

    def run_from_file(self, valid_options=valid_options, sep='_'):
        BLAST.run_from_file("blastn", valid_options, sep)

class BLASTp(BLAST):
    """Subclass for BLASTp searches"""
    blastp_options = ['word_size', 'gapopen', 'gapextend', 'matrix',
        'threshold', 'comp_based_stats', 'seg', 'soft_masking',
        'lcase_masking', 'db_soft_mask', 'db_hard_mask',
        'xdrop_gap_final', 'window_size', 'use_sw_tback']
    valid_options = BLAST.valid_options.extend(blastp_options)

    def run_from_file(self, valid_options=valid_options, sep='_'):
        BLAST.run_from_file(self, "blastp", valid_options, sep)

    def run_from_stdin(self, valid_options=valid_options, sep='_'):
        BLAST.run_from_stdin(self, "blastp", valid_options, sep)
