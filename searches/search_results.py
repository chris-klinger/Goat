"""
Module explanation
"""

import os

from Bio import SeqIO

from searches import search_database, search_util
#from util.inputs import prompts

def seq_from_result(result_name, location=None, evalue_cutoff=None):
    """Creates a sequence file for each Result object in a given database"""
    result_db = search_database.ResultsDB(result_name)
    for result in result_db.list_results():
        result_obj = result_db.fetch_result(result)
        desired_seqs = []
        outfile = os.path.join(location, (result_obj.identity + 'seqs.fa'))
        db = result_obj.database
        for hit in result_obj.parsed_obj.descriptions:
            desired_seqs.append(search_util.remove_blast_header(hit.title))
        #print(desired_seqs)
        with open(outfile,'w') as o:
            for record in SeqIO.parse(db, "fasta"):
                if record.description in desired_seqs:
                    SeqIO.write(record, o, "fasta")

def seq_from_summary():
    """Creates a sequence file for a given Summary object"""
    pass

