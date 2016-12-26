"""
Module explanation
"""

import os

from Bio import SeqIO

from searches import search_database, search_util
#from util.inputs import prompts

# Can hopefully delete after testing
def seq_from_result_old(result_name, location=None, evalue_cutoff=None):
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

def seqs_from_result(result_obj):
    """Returns a list of seqrecord objects"""
    desired_seqs = []
    seq_records = []
    db = result_obj.database
    for hit in search_util.parse_output_file(result_obj.location).descriptions:
        new_title = search_util.remove_blast_header(hit.title)
        if not new_title in desired_seqs:
            desired_seqs.append(new_title)
    for record in SeqIO.parse(db, "fasta"):
        if record.description in desired_seqs:
            seq_records.append(record)
    return seq_records

def seqfile_from_result_db(result_name, location=None, evalue_cutoff=None):
    """Writes sequences to an output file"""
    result_db = search_database.ResultsDB(result_name)
    for result in result_db.list_results():
        result_obj = result_db.fetch_result(result)
        outfile = os.path.join(location, (result_obj.identity + 'seqs.fa'))
        with open(outfile,'w') as o:
            for record in seqs_from_result(result_obj):
                SeqIO.write(record, o, "fasta")

def seq_from_summary():
    """Creates a sequence file for a given Summary object"""
    pass

