"""
This module contains classes to model various kinds of HMMer searches that can be
carried out through the Goat interface. Can probably do both protein and nucl
searches through a common superclass, even though these are technically separate
programs within the HMMer package.
"""

import os, subprocess

class HMMer():
    """
    Parental HMMer class from which all (HMM-based and non-iterative) HMMer
    subclasses derive. Parameters specific to one or more flavours of HMMer
    are delegated to that subclass instead.
    """
    valid_options = ['h', 'o', 'A', 'tblout', 'dfamtblout', 'acc', 'noali',
            'notextw', 'textw', 'E', 'T', 'incE', 'incT', 'cut_ga', 'cut_nc',
            'cut_tc', 'max', 'F1', 'F2', 'F3', 'nobias', 'nonull2', 'Z', 'seed',
            'cpu', 'stall', 'mpi']

    def __init__(self, hmmer_path, query, db, out, **kwargs):
        self.hmmer_path = hmmer_path
        self.query = query
        self.db = db
        self.out = out
        self.kwargs = kwargs

    def get_uniq_out(self, sep):
        """Gets a unique output file name"""
        db_name = os.path.basename(self.db)
        out_string = str(self.query.identity + sep + db_name + sep + 'out.txt')
        return os.path.join(self.out, out_string)

    def run_from_file(self, hmmer_type, valid_options=valid_options, sep='_'):
        """Runs HMMer using file as input"""
        args = []
        args.append(os.path.join(self.hmmer_path, hmmer_type))
        # now add some arguments
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options:
                    if len(k) == 1:
                        args.append('-' + str(k)) # only single hyphen for flag
                    else:
                        args.append('--' + str(k))
                    args.append(str(v))
        args.extend([self.query.location, self.db])
        try:
            subprocess.run(args)
        except(Exception): # all but sys exits
            pass # freak out

    def run_from_stdin(self, hmmer_type, valid_options=valid_options, sep='_'):
        """Runs HMMer using obj as stdin"""
        args = []
        args.append(os.path.join(self.hmmer_path, hmmer_type))
        # specify the tabular output file
        args.append('--tblout')
        args.append(self.out)
        # now add some arguments
        if self.kwargs:
            for k,v in self.kwargs:
                if str(k) in valid_options:
                    if len(k) == 1:
                        args.append('-' + str(k)) # only single hyphen for flag
                    else:
                        args.append('--' + str(k))
                    args.append(str(v))
        args.extend(['-', self.db]) # '-' signals hmmer to expect input from stdin
        try:
            hmmer = subprocess.Popen(args, stdin=subprocess.PIPE)
            # send file as stdin
            hmmer.stdin.write(self.query.sequence.encode('utf-8')) # sequence here is the entire parsed file
            hmmer.communicate() # actually run the search
        except(Exception):
            pass # freak out


class ProtHMMer(HMMer):
    """Subclass for searching protein queries with HMMer"""
    hmmprot_options = ['domE', 'domT', 'incdomE', 'incdomT', 'domZ', 'tformat']
    valid_options = HMMer.valid_options.extend(hmmprot_options)

    def run_from_file(self, valid_options=valid_options, sep='_'):
        HMMer.run_from_file(self, 'hmmsearch', valid_options, sep)

    def run_from_stdin(self, valid_options=valid_options, sep='_'):
        HMMer.run_from_stdin(self, 'hmmsearch', valid_options, sep)

class NuclHMMer(HMMer):
    """Subclass for searching nucelotide queries with HMMer"""
    pass


