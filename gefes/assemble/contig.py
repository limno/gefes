# Futures #
from __future__ import division

# Built-in modules #

# Internal modules #
from plumbing.autopaths import AutoPaths
from plumbing.cache import property_cached

# Third party modules #

###############################################################################
class Contig(object):
    """A contig as predicted by the assembler. It has for instance a nucleotide frequency."""

    all_paths = """
    /lorem.txt
    /genes/
    """

    def __repr__(self): return '<%s object "%s">' % (self.__class__.__name__, self.name)

    def __init__(self, assembly, record, num=None):
        # Save parent #
        self.parent, self.assembly = assembly, assembly
        # Basic attributes #
        self.record = record
        self.name = self.record.id
        self.num = num
        # Auto paths #
        self.base_dir = self.parent.base_dir
        self.p = AutoPaths(self.base_dir, self.all_paths)

    @property
    def length(self):
        return len(self.record.seq)

    @property
    def gc_content(self):
        pass

    def get_nuc_freq(self, windowsize):
        """Returns frequency of nucelotide in this contig with length windowsize"""
        freqs = {}
        allowed_nucs = {'A': 0, 'C': 0, 'G': 0, 'T': 0}
        is_nuc = lambda x: x in allowed_nucs
        upper = str(self.record.seq).upper()
        i = 0
        while i < len(upper) - windowsize + 1:
            nuc_win = upper[i:i + windowsize]
            # check if all nucleotides in the window are A,C,G or T
            for j, n in enumerate(nuc_win):
                if not is_nuc(n):
                    i += j + 1
                    break
            else:
                # if no break add nuc_win count
                freqs[nuc_win] = freqs.get(nuc_win, 0) + 1
                i += 1
        # normalize counts by number of windows to get frequency
        for nuc_win in freqs:
            freqs[nuc_win] = freqs[nuc_win] / float(self.length - windowsize + 1)
        return freqs

    @property_cached
    def tetra_nuc_freq(self):
        return self.get_nuc_freq(3)

