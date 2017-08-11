"""
Provides an initialization framework for Goat in a new directory.

Consists of the following functions:
'initialize_goat()' - runs the other two functions
'check_goat()' - checks whether a Goat subdirectory already exists and
returns True, else returns False
'make_goat()' - builds a Goat subdirectory structure if required
"""

import os, pickle

from settings import settings_file
from databases import goat_db
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
    initialize_settings(base_dir)
    initialize_dbs(base_dir)
    # Add a global thread counter
    configs['threads'] = util.ThreadCounter()

def initialize_settings(base_dir):
    """Checks for a settings file"""
    sfile = os.path.join(base_dir, 'settings/goat_settings.pkl')
    if os.path.exists(sfile):
        pass
    else:
        create_settings(sfile)
    sobj = settings_file.SettingsFile(sfile)
    configs['settings'] = sobj # add to dictionary for re-write

def create_settings(sfile):
    """Creates the initial settings file"""
    with open(sfile, 'wb') as o:
        settings = settings_file.Settings()
        pickle.dump(settings, o)

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
    configs['query_db'] = dbs.QueryDB()
    configs['misc_queries'] = dbs.MiscQDB()
    configs['search_queries'] = dbs.SearchQDB()
    configs['query_sets'] = dbs.QSetDB()
    configs['record_db'] = dbs.RecordDB()
    configs['result_db'] = dbs.ResultDB()
    configs['search_db'] = dbs.SearchDB()
    configs['summary_db'] = dbs.SummaryDB()
