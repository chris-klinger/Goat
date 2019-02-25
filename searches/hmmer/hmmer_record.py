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
        self.e = float(evalue)
        self.score = float(score)
        self.bias = float(bias)
        self.dom_evalue = float(dom_evalue)
        self.dom_score = float(dom_score)
        self.dom_bias = float(dom_bias)
        self.exp = float(exp)
        self.reg = int(reg)
        self.clu = int(clu)
        self.ov = int(ov)
        self.env = int(env)
        self.dom = int(dom)
        self.rep = int(rep)
        self.inc = int(inc)
        self.desc = desc
        if self.desc == '-': # not simply '', hmmer writes as '-'
            self.title = self.target_name # all of the title is in the name
        else:
            self.title = (self.target_name + ' ' + self.desc) # stay consistent with BLAST

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


