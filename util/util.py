"""
This module contains miscellaneous supporting classes/functions for use throughout
Goat.
"""

import threading

###################
# Utility classes #
###################

class IDCounter:
    """
    Provides a counter/container for generating unique IDs for use in Treeview
    trees and other areas where unique identifiers are required.
    """
    def __init__(self, value=0):
        self._value = None
        self.value = value

    def get_id(self):
        """Provides the current value of self.value"""
        return self.value

    def increment(self):
        """Increments counter by 1 to generate new unique ID"""
        self.value += 1

    def get_new_id(self):
        """Yield current id and increment"""
        self._value = self.value
        self.increment()
        return self._value

class ThreadCounter:
    def __init__(self):
        self.num_threads = 0
        self._lock = threading.Lock()

    def add_thread(self):
        """Adds a thread to the object; access is restricted by a lock to prevent
        concurrent access; for instance on threads finishing"""
        with self._lock:
            self.num_threads += 1

    def remove_thread(self):
        """Removes a thread with safe access"""
        with self._lock:
            self.num_threads -= 1

    def exist(self):
        """Simple convenicence function that returns True if the count of active
        threads is greater than 0 and False otherwise"""
        if self.num_threads > 0:
            return True
        return False

#####################
# Utility functions #
#####################

def split_input(instring, chunk_size=60): # 60 default for BioPython FASTA
    """
    Splits a string into a number of sub-strings of length 'chunk_size' as a list;
    does not worry about splitting on words, etc. Final chunk will be less than or
    equal to 'chunk_size'; Used for writing FASTA-style input
    """
    num_chunks = len(instring)//chunk_size # '//' for python3, rounds off
    if (len(instring) % chunk_size != 0):
        num_chunks += 1
    output = []
    for i in range(num_chunks):
        output.append(instring[chunk_size*i:chunk_size*(i+1)])
    return output
