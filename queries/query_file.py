"""
This module contains code for adding queries from a file. It should take a filepath
and type, a reference to an open database, and some other basic information in order
to parse the file correctly and then add the resulting queries to the database.

For now, start with just FASTA files, but eventually should accommodate other file
types and also MSA-based files (although here the file itself might be the sole
reference to the query itself).
"""

#from queries import query_obj
from queries import query_objects

class QueryFile():
    """Generic class for a file to add queries from
    NB: previously had an attribute for 'filetype', in order to provide info
    regarding subclass usage, but likely better to do something in a separate
    class eventually that instantiates a subclass based on the type"""
    def __init__(self, filepath, db_type,
            record=None, self_blast=None):
        self.filepath = filepath
        self.db_type = db_type
        self.record = record
        self.self_blast = self_blast

    def parse(self):
        """Implement in subclass"""
        pass

    def add_queries(self):
        """Implement in subclass"""
        pass

class FastaFile(QueryFile):
    """FASTA-format class for adding FASTA queries"""
    def parse(self):
        """Uses BioPython to parse file and returns a lazy generator for
        all entries within that file"""
        from Bio import SeqIO
        return SeqIO.parse(self.filepath, "fasta")

    def get_queries(self):
        """Adds parsed queries to returned data structure"""
        queries = []
        for seq_record in self.parse():
            qobj = query_objects.SeqQuery(
                        identity=seq_record.id,
                        name=seq_record.name,
                        description=seq_record.description,
                        location=self.filepath,
                        alphabet=self.db_type,
                        sequence=seq_record.seq,
                        record=self.record,
                        racc_mode=self.self_blast)
            queries.append([seq_record.id, qobj])
        return queries

class HMMFile(QueryFile):
    """HMM-format class for adding HMM queries"""
    def parse(self):
        """Somewhat naive, assumes only one query per file"""
        with open(self.filepath,'U') as f:
            return f.read()

    def get_query(self):
        """Just returns a single query object"""
        hmm_obj = self.parse()
        import re
        m = re.search(r'NAME\s+(\w+)', hmm_obj) # matches NAME field of header
        name = m.group(1)
        qobj = query_objects.HMMQuery(
                    identity=name,
                    name=name,
                    description=name,
                    location=self.filepath,
                    alphabet=self.db_type,
                    sequence=hmm_obj)
        return (name,qobj)
