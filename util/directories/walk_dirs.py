"""
Contains a class-style interface for traversing and dealing with
directory tree structures.
"""

import os

class Walker:
    """
    Uses the underlying os module functions to walk directory trees,
    keeping track of directories and files visited. Default starting
    directory is current directory. Subclasses can override and extend
    functionality to search for specific file extensions, context
    within files, and process files.
    """

    def __init__(self, start_dir=None, exts=None, context=None):
        self.file_count = 0
        self.dir_count = 0
        self.start_dir = os.curdir if start_dir is None else start_dir
        self.exts = exts
        self.context = context

    def run(self, reset=True):
        if reset:
            self.reset()
        for (dirpath, dirnames, filenames) in os.walk(self.start_dir):
            self.visitdir(dirpath)
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                self.visitfile(filepath)

    def reset(self):
        """Reset counters each time"""
        self.file_count = self.dir_count = 0

    def visitdir(self, dirpath):
        """Subclasses should extend this method"""
        self.dir_count += 1

    def visitfile(self, filepath):
        """Subclasses should extend this method"""
        self.file_count += 1

class SeqDBWalker(Walker):
    """
    Extends the Walker class to list out information about seqdb records;
    these represent nested directory structures and so should be dealt
    with in a top-down nested fashion.
    """

    def visitdir(self, dirpath):
        """Lists out visited directories"""
        self.dir_count += 1
        print('=>' + dirpath)

    def visitfile(self, filepath):
        """Lists out visited files"""
        self.file_count += 1
        print('==>' + filepath)

    def numcounts(self):
        """Returns the tuple dircounts, filecounts"""
        return (self.dir_count, self.file_count)
