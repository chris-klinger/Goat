"""
Contains a class-style interface for traversing and dealing with
directory tree structures.
"""

import os, glob

class Walker:
    """
    Uses the underlying os module functions to walk directory trees,
    keeping track of directories and files visited. Default starting
    directory is current directory. Subclasses can override and extend
    functionality to search for specific file extensions, context
    within files, and process files.
    """

    def __init__(self, start_dir=None, *exts):
        self.file_count = 0
        self.dir_count = 0
        self.start_dir = os.curdir if start_dir is None else start_dir
        self.exts = exts

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

class FileWalker(Walker):
    """
    Extends the Walker class to gather a list of files in nested directory
    structures. If 'exts' is specified, will only gather files with an
    extension matching one or more provided options
    """

    def __init__(self, start_dir=None, recurse=False, *exts):
        self.file_count = 0
        self.dir_count = 0
        self.recurse = recurse
        self.to_add = []
        Walker.__init__(self, start_dir, *exts)

    def run(self, reset=True):
        if reset:
            self.reset()
        if self.recurse:
            for (dirpath, dirnames, filenames) in os.walk(self.start_dir):
                self.visitdir(dirpath)
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if not filename.startswith('.'): # ignore hidden files
                        self.visitfile(filepath)
        else:
            filepaths = os.path.join(self.start_dir, '*')
            for afile in glob.glob(filepaths):
                if not os.path.basename(afile).startswith('.'): # ignore hidden files
                    self.visitfile(filepath)

    def visitfile(self, filepath):
        """Adds files seen to a list"""
        if not self.exts:
            self.to_add.append(filepath)
        elif self.exts:
            new_exts = []
            for ext in self.exts:
                if '.' in ext: # already includes period symbol
                    new_exts.append(str(ext.rsplit('.',1)[1]))
                else:
                    new_exts.append(str(ext))
            for ext in new_exts:
                if ext == str(filepath.rsplit('.',1)[1]):
                    self.to_add.append(filepath)

    def getfiles(self):
        """Utility function to run the walker and return files"""
        self.run()
        return self.to_add
