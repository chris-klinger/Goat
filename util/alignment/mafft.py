"""
This module contains code for aligning sequences using MAFFT. Idea is to have a
single class that handles both files and stdin.
"""

import os,subprocess

# Should eventually go through settings
tmp_dir = '/Users/cklinger/git/Goat/tmp'

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
        self.check_input_file()
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
            #e_file = open(self.get_tmp_output(),'wb')
            #print("Running mafft for {}".format(self.seq_file))
            # Somehow a PIPE works better here than an output file?
            subprocess.run(args, stdout=o_file,
                    stderr=subprocess.PIPE) # prevents clogging terminal window
            #mafft_line = 'mafft-linsi ' + str(self.seq_file) + ' > ' + str(self.msa_file)
            #p = subprocess.Popen(mafft_line, shell=True)
            #p.communicate()
        except(Exception):
            print("Could not run MAFFT for {}".format(
                self.seq_file))

    def run_from_stdin(self):
        """Calls mafft using sequences from input stream"""
        pass # to be implemented

    def get_tmp_output(self):
        """
        Unsure, but trying - eventual idea would be to redirect stderr to a log
        file but for now just want to dump it somewhere that is not the terminal
        window (annoying for debugging purposes).
        """
        if not self.msa_file:
            self.msa_file = self.seq_file.rsplit('.',1)[0] + '.mfa'
        return os.path.join(tmp_dir,self.msa_file)

    def check_input_file(self):
        """
        Checks input file for illegal characters and replaces them with gap
        characters instead.
        """
        new_file = self.seq_file.rsplit('.',1)[0] + '_filtered.fa'
        with open(self.seq_file,'U') as i, open(new_file,'w') as o:
            for line in i:
                if not line.startswith('>'):
                    line = line.replace('.','-')
                o.write(line)
        self.seq_file = new_file
