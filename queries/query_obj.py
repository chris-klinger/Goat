"""
New module for dealing with query objects
"""

import os
from tkinter import messagebox

from persistent import Persistent
from Bio.Blast import NCBIXML

#from databases import database_config
from searches.blast import blast_setup
#from records import record_db
#from databases import goat_db

# placeholder, eventually through settings
blast_path = '/usr/local/ncbi/blast/bin'
tmp_dir = '/Users/cklinger/git/Goat/tmp'
#goat_db = database_config.get_goat_db()
#record_db = database_config.get_record_db(goat_db)
#record_db = record_db.RecordDB(goat_db.GoatDB(os.path.join('Users/cklinger/git/Goat/tmp',
#    'DB', 'new_goat_db.fs')))

class Query(Persistent):
    """Generic Query class"""
    def __init__(self, identity, name=None, description=None, location=None,
            search_type=None, db_type=None, sequence=None, record=None,
            racc_mode=None, search_ran=False, target_db=None, original_query=None):
        self.identity = identity
        self.name = name
        self.description = description
        self.location = location
        self.search_type = search_type
        self.db_type = db_type
        self.sequence = sequence
        self.record = record
        # Next entries for dealing with redundant accessions
        self.racc_mode = racc_mode
        self.search_ran = search_ran # checks whether search has been run
        self.all_accs = [] # list of all associated search hits; initially empty
        self.redundant_accs = [] # list of chosen raccs; initially empty
        # Next entries for reverse searches
        self.target_db = target_db # used for reverse searches
        self.original_query = original_query

    def run_self_blast(self, record_db):
        """Runs a BLAST search against own record_db"""
        try:
            if self.search_ran: # search has been run already, overwrite?
                if messagebox.askyesno(
                    message = "Self-BLAST has already been run for {}, rerun?".format(self.identity),
                    icon='question', title='Override Search Results'):
                    pass # keep going
                else:
                    raise(Exception) # update to more specific case later
            #print(self.record)
            record_obj = record_db[self.record]
            #record_obj = record_db.__get__item('Hsapiens')
            target_db = None
            for fobj in record_obj.files.values():
                if fobj.filetype == self.db_type: # must match, e.g. prot to prot
                    target_db = fobj.filepath
            if target_db is None:
                raise(Exception) # update to more specific case later
            outpath = os.path.join(tmp_dir, (str(self.identity) + '_BLAST.txt'))
            if self.db_type == 'protein':
                blast_search = blast_setup.BLASTp(
                    blast_path, self, target_db, outpath)
            elif self.db_type == 'genomic':
                pass # need to do for all?
            blast_search.run_from_stdin()
            self.add_self_blast(outpath)
            self.search_ran = True
            if self.racc_mode == 'auto':
                pass # call another function
        except: # Need to make more specific in future
            pass # do something

    def add_self_blast(self, filepath):
        """Parses and adds the object to self attribute"""
        self.all_accs = NCBIXML.read(open(filepath))

    def modify_raccs(self, *accs):
        """Sets attribute to new list"""
        self.redundant_accs = list(accs)
