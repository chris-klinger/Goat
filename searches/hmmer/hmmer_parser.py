"""
This module contains code for parsing tabular HMMer output files. Note that
different parse routines are required for --tblout files of both hmmsearch and
nhmmer, and also probably for other programs such as phmmer.
"""

from util.directories import dirfiles
from hmmer_record import *

class HMMerParser:
    """
    Superclass for HMMer parsers that defines two methods:

    read() - that reads an open file handle and packages all lines into a list

    parse() - generates objects from read(); must be defined by subclasses
    """
    def __init__(self, filepath):
        self.filepath = filepath

    def read(self):
        """Read non-blank lines after skipping header"""
        parsed_lines = []
        with open(self.filepath,'U') as f:
            for line in dirfiles.nonblank_lines(f):
                if not line.startswith('#'): # skip header lines
                    llist = line.split()
                    parsed_lines.append(llist)
        return parsed_lines

    def parse(self):
        """Must be overridden in subclass"""
        raise NotImplementedError

class HMMsearchParser(HMMerParser):
    """Subclass to parse the main protein search output of HMMer."""
    def parse(self):
        """Iterates over lines in file to create an object"""
        record = HMMerRecord('protein')
        for entry in self.read():
            descr = ProtDescr(*entry) # should unpack list of lists into args?
            record.add_description(descr)

class NHMMerParser(HMMerParser):
    """Subclass to parse the main protein search output of HMMer."""
    def parse(self):
        """Iterates over lines in file to create an object"""
        record = HMMerRecord('nucleotide')
        for entry in self.read():
            descr = ProtDescr(*entry) # should unpack list of lists into args?
            record.add_description(descr)
