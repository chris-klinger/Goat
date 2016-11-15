"""
Module explanation.
"""

from blast import blast_setup
import pickle

class Search:
    """Generic search object. Interaction is through a separate class."""
    def __init__(self, search_type, queries, databases, *params):
        self.search_type = search_type
        self.queries = queries # pointer to the shelve object containing the instances
        self.databases = databases
        self.params = params

class SearchFile:
    """Interface for the underlying search object"""
    def __init__(self, search_name):
        self.__dict__['search_name'] = search_name

    def run(self):
        """Runs the actual search specified by the search file"""
        query_db = self.__getattr__('queries')
        for query in query_db.list_queries():
            for db in self.__getattr__('databases'):
                if self.__getattr__('search_type') == 'BLAST':
                    if self.__getattr__('search_type') == 'protein':
                        blast_search = blast_setup.BLASTp("path_to_blast", # placeholder
                            query.location, db, "outfile path")
                    elif self.__getattr__('search_type') == 'genomic':
                        pass # should change depending on search type
                    blast_search.run()

    def parse():
        """Parses the search output"""
        pass

    def execute():
        """Convenience function to run searches and parse output"""
        pass

    def __getattr__(self, attr):
        """Gets attribute from settings object"""
        try:
            search_file = open(self.db_name, 'rb')
            settings = pickle.load(search_file)
            return getattr(settings, attr)
        except(AttributeError):
            print('No such search setting as {}'.format(attr))
        finally:
            search_file.close()

    def __setattr__(self, attr, value):
        """Sets attributes of settings object"""
        read_file = open(self.db_name, 'rb')
        search = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.db_name, 'wb')
            setattr(search, attr, value)
            pickle.dump(search, write_file)
        except(Exception):
            print('Error when writing search setting {}'.format(attr))
        finally:
            write_file.close()

    def __delattr__(self, attr):
        """Deletes attribute from settings object"""
        read_file = open(self.db_name, 'rb')
        search = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.db_name, 'wb')
            delattr(search, attr)
            pickle.dump(search, write_file)
        except(Exception):
            print('Error when deleting search setting {}'.format(attr))
        finally:
            write_file.close()

    def list_attrs(self):
        """Returns a list of all attributes from search object"""
        read_file = open(self.db_name, 'rb')
        search = pickle.load(read_file)
        try:
            return search.__dict__.items()
        except(Exception):
            print('Error when accessing search settings')
        finally:
            read_file.close()
