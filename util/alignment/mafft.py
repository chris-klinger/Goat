"""
This module contains code for aligning sequences using MAFFT. Idea is to have a
single class that handles both files and stdin.
"""

import os,subprocess

class MAFFT:
    def __init__(self, seq_file, msa_file=None, *kwargs):
        self.seq_file = seq_file
        self.msa_file = msa_file
        self.kwargs = kwargs

    def get_msa_name(self):
        """Gets name if not specified by user"""
        if not self.msa_file:
            self.msa_file = self.seq_file.rsplit('.',1)[0] + '.mfa'
        target_dir = os.path.split(self.seq_file)[0]
        self.msa_file = os.path.join(target_dir,self.msa_file)

    def run(self, mode):
        """Choose to run"""
        self.get_msa_name()
        if mode == 'file':
            self.run_from_file()
        elif mode == 'stdin':
            self.run_from_stdin()

    def run_from_file(self):
        """Calls mafft on a target file"""
        args = []
        args.extend(['mafft-linsi', self.seq_file])
        if self.kwargs:
            for k,v in self.kwargs:
                args.append('--' + str(k)) # need to check this
                args.append(str(v))
        try:
            # cannot use shell redirects, instead set stdout as target file
            o_file = open(self.msa_file,'wb')
            print("Running mafft for {}".format(self.seq_file))
            subprocess.run(args, stdout=o_file)
        except(Exception):
            print("Could not run MAFFT for {}".format(
                self.seq_file))

    def run_from_stdin(self):
        """Calls mafft using sequences from input stream"""
        pass # to be implemented
