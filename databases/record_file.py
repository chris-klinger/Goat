"""
This module contains code for dealing with files in records. As opposed to before
where files were modelled as single attribute/value pairs, they will now take on
a more serious implementation including a class-based system (starting just with
a basic FASTA class) for expansibility, but also to have knowledge of some of
their own metadata as well.
"""

from persistent import Persistent

class File(Persistent):
    """
    Generic file class to store information about files. Subclasses may need
    to override methods, depending on how their structure differs.
    """
    def __init__(self, name='', filepath='', filetype=None, size=0, num_entries=0,
            num_lines=0, num_bases=0):
        self.separator = None # e.g. '>' in FASTA
        self.name = name
        self.filepath = filepath
        self._cached_file = ''
        self.filetype = filetype
        self.size = 0
        self.num_entries = num_entries
        self.num_lines = num_lines
        self.num_bases = num_bases
        self.update_file()

    def update_file(self):
        """
        Convenience function, runs on first instantiation and then whenever the
        associated file changes path, either to point at the same file or to a
        different file (to be safe)
        """
        if self._cached_file == self.filepath:
            return
        self.get_size()
        self.calc_properties()

    def get_size(self):
        """Sets the size of the associated file"""
        import os
        try:
            self.size = os.stat(self.filepath).st_size
        except:
            pass # sets nothing

    def calc_properties(self):
        """
        Function that gets information about various file attributes. A single
        call steps through the entire file at once and calculates the number
        of entries, lines, and bases
        """
        from util.directories import dirfiles
        try:
            tmp_entries = 0
            tmp_lines = 0
            tmp_bases = 0
            with open(self.filepath,'U') as i:
                for line in dirfiles.nonblank_lines(i):
                    tmp_lines += 1
                    if line.startswith(self.separator):
                        tmp_entries += 1
                    else:
                        for base in line:
                            tmp_bases += 1
            self.num_entries = tmp_entries
            self.num_lines = tmp_lines
            self.tmp_bases = tmp_bases
        except:
            pass # sets nothing

class FastaFile(File):
    """
    Fasta file implementation. Sets self.separator to '>'
    """
    def __init__(self, name='', filepath='', filetype=None, size=0, num_entries=0,
            num_lines=0, num_bases=0):
        self.separator = '>'
