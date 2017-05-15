#!/usr/bin/env python3

import os, sys

from bin import initialize_goat
from settings import settings_interface
#from databases import database_interface,database_records,record_db
from databases import goat_db
from records import record_db
from searches import search_interface,query_db
from gui import main_gui

goat_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
settings_basename = 'settings/goat_settings.pkl'

def get_settings_file():
    """Returns full pathname to settings file"""
    return os.path.join(goat_dir, settings_basename)

def get_goat_db():
    """Gets the path to the goat database"""
    db_path = os.path.join(goat_dir, 'DB', 'new_goat_db.fs')
    return goat_db.GoatDB(db_path)

def get_record_db(db_obj):
    """Gets the records database"""
    #return database_records.RecordsDB(os.path.join(goat_dir, 'DB','records'))
    #return record_db.RecordDB(os.path.join(goat_dir, 'DB', 'goat_db.fs'))
    return record_db.RecordDB(db_obj)
    #return os.path.join(goat_dir, 'DB', 'goat_db.fs')

def get_query_db(db_obj):
    return query_db.QueryDB(db_obj)

def main_goat():
    initialize_goat.initialize(goat_dir)
    settings_interface.settings_loop(goat_dir)
    database_interface.database_loop(goat_dir)
    search_interface.search_loop(goat_dir)

def goat_gui():
    initialize_goat.initialize()
    main_gui.run()

if __name__ == '__main__':
    #main_goat()
    goat_gui()
