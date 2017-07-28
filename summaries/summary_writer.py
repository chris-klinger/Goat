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
                self.fobj.write(str(block) + ',')
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
        param_list.extend([self.sobj.fwd, self.sobj.fwd_qtype, self.sobj.fwd_dbtype,
            self.sobj.fwd_algorithm, self.sobj.fwd_evalue, self.sobj.fwd_max_hits])
        if self.sobj.rev:
            param_list.extend([self.sobj.rev, self.sobj.rev_qtype, self.sobj.rev_dbtype,
                self.sobj.rev_algorithm, self.sobj.rev_evalue, self.sobj.rev_max_hits])
        param_list.append(self.sobj.next_evalue)
        label_list = ['<PARAM>' for x in param_list] # make a list of labels
        for l,v in zip(label_list, param_list):
            self.info_list.append(l + ' ' + str(v))
            self.write_info()
        self.fobj.write('\n')

    def write_hits(self):
        """Iterates through the summary obj to print relevant information"""
        for qid in self.sobj.query_list:
            qobj = self.sobj.queries[qid]
            for db in qobj.db_list:
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
