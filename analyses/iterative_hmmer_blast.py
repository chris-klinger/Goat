"""
This module contains code to conduct iterative HMMer searches in Goat. From a
starting HMM or MSA, a forward HMMer search is conducted, followed by reverse
BLAST to identify any positive hits. Positive hits are added to the HMM and the
HMMer search is conducted again. This process is iterated until no more hits
are added to the HMM.
"""
