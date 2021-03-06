"""
This module contains code to build an HMM from an input MSA. Eventually, should
be able to work with either stdin or file input, but for now stick to file
input.
"""

import os, subprocess

# Should eventually go through settings
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class HMMBuild():
    """
    A class to interface between Goat and the underlying HMMer program. Since
    the same program is used for different input formats (including nucleotide),
    don't need separate subclasses.
    """
    valid_options = ['h', 'n', 'o', 'O', 'amino', 'dna', 'rna', 'fast', 'hand',
            'symfrac', 'fragthresh', 'wpb', 'wgsc', 'wblosum', 'wnone', 'wid',
            'eent', 'eclust', 'enone', 'eset', 'ere', 'esigma', 'eid', 'pnone',
            'plaplace', 'EmL', 'EmN', 'EvL', 'EvN', 'EfL', 'EfN', 'Eft', 'cpu',
            'informat', 'seed', 'w_beta', 'w_length', 'mpi', 'stall',
            'maxinsertlen']

    def __init__(self, hmmbuild_path, msa_filepath, hmm_out, **kwargs):
        self.build_path = hmmbuild_path
        self.msapath = msa_filepath
        self.hmm_out = hmm_out # outpath for target file
        self.kwargs = kwargs

    def run_from_file(self, valid_options=valid_options):
        """Runs the program"""
        args = []
        args.append(os.path.join(self.build_path, 'hmmbuild'))
        # add arguments
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options:
                    if len(k) == 1:
                        args.append('-' + str(k)) # single hyphen for single letter args
                    else:
                        args.append('--' + str(k))
                    args.append(str(v))
        args.extend([self.hmm_out, self.msapath])
        try:
            e_file = open(self.get_tmp_output(),'wb')
            # Redirect both stdout and stderr to a file
            # Args send stdout to self.hmm_out but the process stdout still
            # Prints to the terminal despite this
            subprocess.run(args, stdout=e_file,
                    stderr=e_file)
        except(Exception): # all but sys exits
            pass # freak out

    def get_tmp_output(self):
        """File for stderr redirection"""
        basename = os.path.basename(self.msapath)
        outname = basename + '.txt'
        return os.path.join(tmp_dir,outname)
