"""
Module explanation.
"""

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

    def run():
        """Runs the actual search specified by the search file"""
        pass

    def parse():
        """Parses the search output"""
        pass

    def execute():
        """Convenience function to run searches and parse output"""
        pass
