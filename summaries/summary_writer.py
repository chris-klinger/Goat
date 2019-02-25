"""
This module contains classes for writing csv tabular output in Goat, for both result
summaries and summaries of multiple summaries. Should eventually make output
customizable for user-chosen parameters, such as including search parameters in the
final output or not.
"""

class ResultSummaryWriter:
    def __init__(self, summary_obj, fobj):
        self.sobj = summary_obj
        self.fobj = fobj
        self.info_list = []

    def write(self):
        """Writes the information and closes the file"""
        try:
            self.write_params()
            self.write_hit_header()
            self.write_hits()
        except:
            print('Error in write()')
            pass # maybe do something?
        finally:
            self.fobj.close() # close file no matter what

    def write_info(self):
        """Writes one line of information to the outfile"""
        try:
            for block in self.info_list:
                san_block = self.sanitize_block(str(block), [','])
                self.fobj.write(san_block + ',')
            self.fobj.write('\n') # new line
        except: # Specific error here?
            try:
                self.fobj.write('Encountered write error')
                self.fobj.write('\n')
            except: # Couldn't even write this
                pass # Do nothing
        finally:
            self.info_list = [] # reset list value no matter what

    def write_params(self):
        """Writes parameter information for summary"""
        param_list = []
        param_list.extend(['Forward Search Name: ' + str(self.sobj.fwd),
            'Forward Query Alphabet: ' + str(self.sobj.fwd_qtype),
            'Forward Database Alphabet: ' + str(self.sobj.fwd_dbtype),
            'Forward Search Algorithm: ' + str(self.sobj.fwd_algorithm),
            'Forward Search Evalue Cutoff: ' + str(self.sobj.fwd_evalue),
            'Number of Hits Checked in Forward Search: ' + str(self.sobj.fwd_max_hits)])
        if self.sobj.rev:
            param_list.extend(['Reverse Search Name: ' + str(self.sobj.rev),
                'Reverse Query Alphabet: ' + str(self.sobj.rev_qtype),
                'Reverse Database Alphabet: ' + str(self.sobj.rev_dbtype),
                'Reverse Search Algorithm: ' + str(self.sobj.rev_algorithm),
                'Reverse Search Evalue Cutoff: ' + str(self.sobj.rev_evalue),
                'Number of Hits Checked in Reverse Search: ' + str(self.sobj.rev_max_hits)])
        param_list.append('Between-Hit Evalue Cutoff: ' + str(self.sobj.next_evalue))
        label_list = ['<PARAM>' for x in param_list] # make a list of labels
        for l,v in zip(label_list, param_list):
            self.info_list.append(l + ' ' + str(v))
            self.write_info()
        self.fobj.write('\n')

    def write_hit_header(self):
        """Writes a header line for hits"""
        header_list = []
        header_list.extend(['Query ID', 'Query Databse', 'Target Database',
                'Database Status', 'Hit Status', 'Fwd Hit ID', 'Fwd Hit Evalue',
                'First Positive Rev Hit ID', 'First Positive Rev Hit Evalue',
                'First Negative Rev Hit ID', 'First Negative Rev Hit Evalue',
                'Evalue Diff Between Pos and Neg Hits'])
        self.info_list = header_list
        self.write_info()
        self.fobj.write('\n')

    def write_hits(self):
        """Iterates through the summary obj to print relevant information"""
        for qid in self.sobj.query_list:
            qobj = self.sobj.queries[qid]
            for db in sorted(qobj.db_list): # sort DBs in alphabetical order?
                db_obj = qobj.dbs[db]
                if db_obj.status == 'negative':
                    self.info_list.extend([qid, db, db_obj.status])
                    self.write_info()
                else:
                    for list_name in db_obj.lists:
                        hlist = getattr(db_obj,list_name)
                        for hit in hlist:
                            self.info_list.extend([qid, db, db_obj.status])
                            hobj = db_obj.hits[hit]
                            self.info_list.extend([hobj.status,
                                hobj.fwd_id, hobj.fwd_evalue,
                                hobj.pos_rev_id, hobj.pos_rev_evalue,
                                hobj.neg_rev_id, hobj.neg_rev_evalue,
                                hobj.rev_evalue_diff])
                            self.write_info()
            self.fobj.write('\n')

    def sanitize_block(self, instring, ill_chars=[], to_replace='_'):
        """
        Takes a string and passes over all characters checking to see if any are
        present in the provided list. If any are, they are replaced by the char
        specified by 'to_replace'.
        """
        out_list = []
        for char in instring:
            if char in ill_chars:
                out_list.append(to_replace)
            else:
                out_list.append(char)
        return ''.join([char for char in out_list])

