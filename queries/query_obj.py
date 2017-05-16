"""
New module for dealing with query objects
"""

from persistent import Persistent
from Bio.Blast import NCBIXML

from searches.blast import blast_setup

# placeholder, eventually through settings
blast_path = '/usr/local/ncbi/blast/bin'

class Query(Persistent):
    """Generic Query class"""
    def __init__(self, identity, name=None, description=None, location=None,
            search_type=None, db_type=None, sequence=None, target_db=None,
            record=None, original_query=None, self_blast=None):
        self.identity = identity
        self.name = name
        self.description = description
        self.location = location
        self.search_type = search_type
        self.db_type = db_type
        self.sequence = sequence
        self.target_db = target_db
        self.record = record
        self.original_query = original_query
        self.self_blast = self_blast
        self.redundant_accs = [] # initialize an empty list

    def run_self_blast(self):
        """Runs a BLAST search against own record_db"""
        if self.self_blast is not None:
            pass # already have BLAST result
        else:
            target_db = 'target' # need to get this somehow
            outpath = 'out' # need to get this somehow
            if self.db_type == 'protein':
                blast_search = blast_setup.BLASTp(
                        blast_path, self, target_db, outpath)
            elif self.db_type == 'genomic':
                pass # need to do for all?
            blast_search.run_from_stdin()
            self.add_self_blast(outpath)

    def add_self_blast(self, filepath):
        """Parses and adds the object to self attribute"""
        self.self_blast = NCBIXML.read(open(filepath))

    def modify_raccs(self, *accs):
        """Sets attribute to new list"""
        self.redundant_accs = list(accs)
