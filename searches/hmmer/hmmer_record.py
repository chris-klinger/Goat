"""
This module contains code for storing the output of tabular HMMer parses, in
analogy to the BLAST record class of BioPython. Idea is to hold on to all of the
possible attributes of a HMMer result so that they can be iterated over after
"""

class HMMerRecord:
    def __init__(self, hmmer_type):
        self.hmmer_type = hmmer_type
        self.descriptions = []

    def add_description(self, desc):
        """Simple convenience function"""
        self.descriptions.append(desc)

class ProtDescr:
    def __init__(self, target_name, target_accession, query_name, query_accession,
            evalue, score, bias, dom_evalue, dom_score, dom_bias, exp, reg, clu,
            ov, env, dom, rep, inc, desc):
        self.target_name = target_name
        self.target_accession = target_accession
        self.query_name = query_name
        self.query_accession = query_accession
        self.evalue = evalue
        self.score = score
        self.bias = bias
        self.dom_evalue = dom_evalue
        self.dom_score = dom_score
        self.dom_bias = dom_bias
        self.exp = exp
        self.reg = reg
        self.clu = clu
        self.ov = ov
        self.env = env
        self.dom = dom
        self.rep = rep
        self.inc = inc
        self.desc = desc

class NuclDescr:
    def __init__(self, target_name, target_accession, query_name, query_accession,
            hmm_from, hmm_to, ali_from, ali_to, env_from, env_to, seq_length,
            strand, evalue, score, bias, desc):
        self.target_name = target_name
        self.target_accession = target_accession
        self.query_name = query_name
        self.query_accession = query_accession
        self.hmm_from = hmm_from
        self.hmm_to = hmm_to
        self.ali_from = ali_from
        self.ali_to = ali_to
        self.env_from = env_from
        self.env_to = env_to
        self.seq_length = seq_length
        self.strand = strand
        self.evalue = evalue
        self.score = score
        self.bias = bias
        self.desc = desc


