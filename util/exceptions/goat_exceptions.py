"""
This module contains custom exceptions to be used throughout Goat.
"""

class ExistsError(Exception):
    """
    Base class for exceptions that arise for pre-existing entities
    that should be held as unique.
    """
    def __init__(self, entity):
        self.entity = entity

    def __str__(self):
        """Must be implemented in subclass"""
        pass

class DirExistsError(ExistsError):
    """A unique directory already exists"""
    def __str__(self):
        return 'Directory already exists: {}'.format(self.entity)

class FileExistsError(ExistsError):
    """A unique file already exists"""
    def __str__(self):
        return 'File already exists: {}'.format(self.entity)
