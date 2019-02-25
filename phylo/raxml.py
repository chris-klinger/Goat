"""
This module contains code for running RAxML in Goat. Initial implementation will be
very simple and allow only to run ScrollSaw.
"""

import subprocess,os

# Go through settings eventually
raxml_path = '/Users/cklinger/src/standard-RAxML-8.1.17/raxmlHPC-AVX'
tmp_dir = '/Users/cklinger/git/Goat/tmp'

class RAxML:
    def __init__(self, infile, outfile, target_dir):
        self.infile = infile
        self.outfile = outfile
        self.target_dir = target_dir

    def get_distances(self):
        """Run RAxML to produce distances"""
        e_file = open(self.get_tmp_output(),'wb')
        subprocess.run([raxml_path, '-f', 'x', '-p', '12345', '-s', self.infile,
            '-m', 'PROTGAMMALG', '-n', self.outfile, '-w', self.target_dir],
            stdout=e_file, stderr=e_file) # does not write to terminal

    def get_tmp_output(self):
        """
        Unsure, but trying - eventual idea would be to redirect stderr to a log
        file but for now just want to dump it somewhere that is not the terminal
        window (annoying for debugging purposes).
        """
        name = self.infile + 'error'
        return os.path.join(tmp_dir,name)
