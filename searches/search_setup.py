"""
Module explanation.
"""

import os,pickle

#from Bio import SearchIO
from Bio.Blast import NCBIXML

from searches.blast import blast_setup

# Placeholder - should be through settings eventually
blast_path = '/usr/local/ncbi/blast/bin'

class Search:
    """Generic search object. Interaction is through a separate class."""
    def __init__(self, search_name=None, search_type=None, queries=[],
            databases=[], db_type=None, keep_output=False, output_location=None,
            results=None, *params):
        self.search_name = search_name
        self.search_type = search_type
        self.queries = queries # pointer to the shelve object containing the instances
        self.databases = databases
        self.db_type = db_type
        self.keep_output = keep_output
        self.output_location = output_location
        self.results = results
        self.params = params

class SearchFile:
    """Interface for the underlying search object"""
    def __init__(self, search_name):
        self.__dict__['search_name'] = search_name

    def get_db_name(self, db_path):
        """Utility function"""
        return os.path.basename(db_path).rsplit('.',1)[0]

    def get_uniq_out(self, query_obj, db_path, sep='-'):
        """Returns a path for a given query and database"""
        out_string = sep.join([query_obj.identity,
                self.get_db_name(db_path),'out.txt'])
        return os.path.join(self.__getattr__('output_location'),out_string)

    def get_result_id(self, query_obj, db_path, sep='-'):
        """Returns a unique name for each result"""
        return sep.join([query_obj.identity,self.get_db_name(db_path)])

    def run_all(self):
        """Runs the actual search specified by the search file"""
        query_db = self.__getattr__('queries')
        result_db = self.__getattr__('results')
        for query in query_db.list_queries():
            #print(query)
            query_obj = query_db.fetch_query(query)
            if query_obj.target_db is not None:
                uniq_out = self.get_uniq_out(query_obj,query_obj.target_db)
                result_id = self.get_result_id(query_obj,query_obj.target_db)
                self.run_one(query_obj,query_obj.target_db,uniq_out,result_db,
                        result_id)
            else: # Need to run for all databases
                for db in self.__getattr__('databases'):
                    #print(db)
                    uniq_out = self.get_uniq_out(query_obj,db)
                    result_id = self.get_result_id(query_obj,db)
                    self.run_one(query_obj,db,uniq_out,result_db,result_id)
                #if self.__getattr__('search_type') == 'BLAST':
                    #print("Running BLAST")
                    #if self.__getattr__('db_type') == 'protein':
                        #print("Protein BLAST")
                        #blast_search = blast_setup.BLASTp(blast_path, # placeholder
                            #query_obj, db, uniq_out)
                    #elif self.__getattr__('search_type') == 'genomic':
                        #pass # should change depending on search type
                    #blast_search.run_from_stdin()
                    #result_db.add_result(self.get_result_id(query_obj,db),
                        #query=query_obj, database=db, location=uniq_out)

    def run_one(self, query_obj, target_db, uniq_out, result_db, result_id):
        """Runs each individual search"""
        if self.search_type == 'BLAST':
            if self.db_type == 'protein':
                blast_search = blast_setup.BLASTp(blast_path,
                    query_obj, target_db, uniq_out)
            elif self.search_type == 'genomic':
                pass
            blast_search.run_from_stdin()
            result_db.add_result(result_id, query=query_obj, database=target_db,
                location=uniq_out)
        elif self.search_type == 'HMMer':
            pass # elaborate later

    def parse(self):
        """Parses the search output"""
        result_db = self.__getattr__('results')
        for result_name in result_db.list_results():
            print(result_name)
            result_obj = result_db.fetch_result(result_name)
            if self.__getattr__('search_type') == 'BLAST':
                # Must use read, not parse! Cannot pickle a generator!!!
                blast_result = NCBIXML.read(open(result_obj.location))
                try:
                    result_db.add_result_info(result_name, parsed_obj=blast_result)
                except Exception:
                    print("Could not update for {}".format(result_name))

    # Might not need this function in the end...
    def execute(self):
        """Convenience function to run searches and parse output"""
        self.run_all()
        self.parse()

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
