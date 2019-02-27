"""
Provides an initialization framework for Goat in a new directory.

Consists of the following functions:
'initialize_goat()' - runs the other two functions
'check_goat()' - checks whether a Goat subdirectory already exists and
returns True, else returns False
'make_goat()' - builds a Goat subdirectory structure if required
"""

import os, pickle

#from settings import settings_file
from databases import goat_db, sets
from settings import settings_obj
#from queries import query_db
#from records import record_db
#from results import result_db
#from searches import search_db
#from summaries import summary_db
from util import util

# global import for database connection
configs = {}

def initialize(base_dir):
    """Runs other initialization functions"""
    #initialize_settings(base_dir)
    # Initialize databases first
    initialize_dbs(base_dir)
    # Initialize settings
    initialize_settings()
    # Add a global thread counter
    configs['threads'] = util.ThreadCounter()

# DEPRECATED
#def initialize_settings(base_dir):
#    """Checks for a settings file"""
#    sfile = os.path.join(base_dir, 'settings/goat_settings.pkl')
#    if os.path.exists(sfile):
#        pass
#    else:
#        create_settings(sfile)
#    sobj = settings_file.SettingsFile(sfile)
#    configs['settings'] = sobj # add to dictionary for re-write
#
#def create_settings(sfile):
#    """Creates the initial settings file"""
#    with open(sfile, 'wb') as o:
#        settings = settings_file.Settings()
#        pickle.dump(settings, o)

def initialize_dbs(base_dir):
    """Checks for required database structure"""
    dbfile = os.path.join(base_dir, 'DB', 'new_goat_db.fs')
    db_obj = goat_db.GoatDB(dbfile)
    configs['goat_db'] = db_obj
    # now get data-type-specific db objects
    get_specific_dbs(db_obj)


def get_specific_dbs(db_obj):
    """Uses the db object to provide pointers to sub-objects"""
    from databases import dbs
    configs['misc_queries']   = dbs.MiscQDB()
    configs['query_db']       = dbs.QueryDB()
    configs['query_sets']     = dbs.QSetDB()
    configs['record_db']      = dbs.RecordDB()
    configs['record_sets']    = dbs.RSetDB()
    configs['result_db']      = dbs.ResultDB()
    configs['search_queries'] = dbs.SearchQDB()
    configs['search_db']      = dbs.SearchDB()
    configs['settings_db']    = dbs.SettingsDB()
    configs['settings_sets']  = dbs.SSetDB()
    configs['summary_db']     = dbs.SummaryDB()


def initialize_settings():
    """
    Run on startup to check for the presence of settings within
    Goat. If no Settings exist, create a basic framework that the
    user can edit.
    """
    ssdb = configs['settings_sets']
    if ssdb.is_empty():  # No sets, therefore no settings
        _create_default_settings()


def _create_default_settings():
    """
    Called to populate initial settings and sets of settings, either
    on startup or if the original data structures are ever removed for
    some reason.

    Need to create a number of settings, each with a default value and
    add them to various sets under the settings_sets db.
    """
    # First specify DBs
    ssdb = configs['settings_sets']
    sdb  = configs['settings_db']
    # Make a single set object
    general = sets.SettingsSet('general')
    # Populate it
    general_settings = [
            ('BLAST path',''),
            ('HMMer path',''),
            ('RAxML path',''),
            ('MAFFT path',''),
            ]
    for name,default in general_settings:
        sobj = settings_obj.Setting(
                name = name,
                value = None,
                default = default,
                )
        # Add object to sdb
        sdb.add_entry(name, sobj)
    # Add all entries at once to set
    general.add_entries([s for s,_ in general_settings])  # Requires a list
    # Finally, add set object to DB
    ssdb.add_entry('general', general)

    # Repeat process for other kinds of settings
    # BLAST-specific
    blast = sets.SettingsSet('blast')
    # Populate it
    blast_settings = [
            ('query_loc',None,1),
            ('evalue',0.05,1),
            ('subject',None,1),
            ('subject_loc',None,1),
            ('show_gis',False,1),
            ('num_descriptions',500,1),
            ('num_alignments',250,1),
            ('max_target_seqs',500,1),
            ('max_hsps',None,1),
            ('html',False,1),
            ('gilist',None,1),
            ('negative_gilist',None,1),
            ('entrez_query',None,1),
            ('culling_limit',None,1),
            ('best_hit_overhang',0.1,1),
            ('best_hit_score_edge',0.1,1),
            ('dbsize',None,1),
            ('searchsp',None,1),
            ('import_search_strategy',None,1),
            ('export_search_strategy',None,1),
            ('parse_deflines',False,1),
            ('num_threads',1,1),
            ('remote',False,1),
            ]
    for name,default,hyphens in blast_settings:
        sobj = settings_obj.Setting(
                name = name,
                value = None,
                default = default,
                num_hyphens = hyphens,
                )
        # Add object to sdb
        sdb.add_entry(name, sobj)
    # Add all entries at once to set
    blast.add_entries([s for s,_,_ in blast_settings])
    # Finally, add set object to DB
    ssdb.add_entry('blast', blast)

    # HMMer-specific
    hmmer = sets.SettingsSet('hmmer')
    # Populate it
    hmmer_settings = [
            ('E',0.05,1),
            ('T',False,1),
            ('domE',10.0,2),
            ('domT',False,2),
            ]
    for name,default,hyphens in hmmer_settings:
        sobj = settings_obj.Setting(
                name = name,
                value = None,
                default = default,
                num_hyphens = hyphens,
                )
        # Add object to sdb
        sdb.add_entry(name, sobj)
    # Add all entries at once to set
    hmmer.add_entries([s for s,_,_ in hmmer_settings])
    # Finally, add set object to DB
    ssdb.add_entry('hmmer', hmmer)

