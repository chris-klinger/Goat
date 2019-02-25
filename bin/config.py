"""
This module contains code to deal with some configuration options in Goat. Unlike
those in the settings file, these are settings that are not intended to be
viewed or modified by the user, but rather are set each time goat is started.

These are set to empty defaults and then changed on program instantiation to real
values, which are then imported by other parts of the program
"""

# main settings file object
settings = ''

# main db file object
goat_db = ''

# db files for other dbs in goat
query_db = ''
record_db = ''
result_db = ''
search_db = ''
summary_db = ''
