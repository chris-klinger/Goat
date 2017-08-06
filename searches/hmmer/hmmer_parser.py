"""
This module contains code for parsing tabular HMMer output files. Note that
different parse routines are required for --tblout files of both hmmsearch and
nhmmer, and also probably for other programs such as phmmer.
"""

from util.directories import dirfiles
from searches.hmmer import hmmer_record

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
                    llist = line.split(maxsplit=18) # otherwise description is also split
                    parsed_lines.append(llist)
        return parsed_lines

    def parse(self):
        """Must be overridden in subclass"""
        raise NotImplementedError

class HMMsearchParser(HMMerParser):
    """Subclass to parse the main protein search output of HMMer."""
    def parse(self):
        """Iterates over lines in file to create an object"""
        record = hmmer_record.HMMerRecord('protein')
        for entry in self.read():
            descr = hmmer_record.ProtDescr(*entry) # should unpack list of lists into args?
            record.add_description(descr)
        return record

class NHMMerParser(HMMerParser):
    """Subclass to parse the main protein search output of HMMer."""
    def parse(self):
        """Iterates over lines in file to create an object"""
        record = hmmer_record.HMMerRecord('nucleotide')
        for entry in self.read():
            descr = hmmer_record.NuclDescr(*entry) # should unpack list of lists into args?
            record.add_description(descr)
        return record
