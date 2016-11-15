"""
Module explanation.
"""

from searches.blast import blast_setup
import pickle

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'

class Search:
    """Generic search object. Interaction is through a separate class."""
    def __init__(self, search_type, queries, databases, db_type,
                keep_output, output_location, *params):
        self.search_type = search_type
        self.queries = queries # pointer to the shelve object containing the instances
        self.databases = databases
        self.db_type = db_type
        self.keep_output = keep_output
        self.output_location = output_location
        self.params = params

class SearchFile:
    """Interface for the underlying search object"""
    def __init__(self, search_name):
        self.__dict__['search_name'] = search_name

    def run(self):
        """Runs the actual search specified by the search file"""
        query_db = self.__getattr__('queries')
        for query in query_db.list_queries():
            print(query)
            query_obj = query_db.fetch_query(query)
            for db in self.__getattr__('databases'):
                print(db)
                if self.__getattr__('search_type') == 'BLAST':
                    print("Running BLAST")
                    if self.__getattr__('db_type') == 'protein':
                        print("Protein BLAST")
                        blast_search = blast_setup.BLASTp(blast_path, # placeholder
                            query_obj.sequence, db, self.__getattr__('output_location'))
                    elif self.__getattr__('search_type') == 'genomic':
                        pass # should change depending on search type
                    blast_search.run()

    def parse(self):
        """Parses the search output"""
        pass

    def execute(self):
        """Convenience function to run searches and parse output"""
        pass

    def __getattr__(self, attr):
        """Gets attribute from settings object"""
        try:
            search_file = open(self.search_name, 'rb')
            search = pickle.load(search_file)
            return getattr(search, attr)
        except(AttributeError):
            print('No such search setting as {}'.format(attr))
        finally:
            search_file.close()

    def __setattr__(self, attr, value):
        """Sets attributes of settings object"""
        read_file = open(self.search_name, 'rb')
        search = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.search_name, 'wb')
            setattr(search, attr, value)
            pickle.dump(search, write_file)
        except(Exception):
            print('Error when writing search setting {}'.format(attr))
        finally:
            write_file.close()

    def __delattr__(self, attr):
        """Deletes attribute from settings object"""
        read_file = open(self.search_name, 'rb')
        search = pickle.load(read_file)
        read_file.close()
        try:
            write_file = open(self.search_name, 'wb')
            delattr(search, attr)
            pickle.dump(search, write_file)
        except(Exception):
            print('Error when deleting search setting {}'.format(attr))
        finally:
            write_file.close()

    def list_attrs(self):
        """Returns a list of all attributes from search object"""
        read_file = open(self.search_name, 'rb')
        search = pickle.load(read_file)
        try:
            return search.__dict__.items()
        except(Exception):
            print('Error when accessing search settings')
        finally:
            read_file.close()
