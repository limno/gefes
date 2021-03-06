# Futures #
from __future__ import division

# Built-in modules #
import re

# Internal modules #
from gefes.preprocess import QualityChecker, QualityResults

# First party modules #
from plumbing.cache import property_cached

# Third party modules #
import sh

###############################################################################
class Sickle(QualityChecker):
    """Takes care of running the sickle program that removes low quality reads.
    The 'singletons' file contains reads that passed the filter in either
    the forward or reverse direction, but not the other.
    Expects version 1.33
    """

    short_name = 'sickle'
    long_name  = 'Sickle cleaner v1.33'
    executable = 'sickle133'
    url        = 'https://github.com/najoshi/sickle/'
    dependencies = []

    threshold   = 20 # This is a PHRED score threshold
    min_length  = 71 # Minimum number of remaining base pairs
    discard_N   = True

    @property
    def window_size(self):
        """You can't chose the window size with sickle.
        It's always 10 percent of read length."""
        return round(len(self.source.fwd.first) * 0.1)

    def run(self):
        # Check version #
        assert "version 1.33" in sh.sickle133('--version')
        # Prepare the command #
        command = ["pe",
                   "-f", self.source.fwd, "-r", self.source.rev,
                   "-o", self.dest.fwd,   "-p", self.dest.rev,
                   "-s", self.singletons,
                   "-l", self.min_length,
                   "-q", self.threshold,
                   "-t", "sanger"]
        if self.discard_N: command += "-n"
        # Call sickle #
        sh.sickle133(*command, _out=self.p.report.path)
        # Count discarded and check #
        self.discarded = self.results.stats['paired_records_discarded']/2
        assert self.results.stats['single_records_discarded'] == self.results.stats['single_records_kept']
        assert self.results.stats['single_records_discarded'] == len(self.singletons)
        # Make other sanity checks #
        assert self.results.stats['paired_records_kept']/2 == len(self.dest.fwd) == len(self.dest.rev)
        assert len(self.source) == len(self.dest) + len(self.singletons) + self.discarded
        # Return result #
        return self.results

    @property_cached
    def results(self):
        results = SickleResults(self, self.source, self.dest, self.singletons)
        if not results: raise Exception("You can't access results from sickle before running the algorithm.")
        return results

###############################################################################
class SickleResults(QualityResults):

    @property_cached
    def stats(self):
        """Parse the report file for statistics"""
        patterns = {'paired_records_kept':      '^FastQ paired records kept: (.+?) .+$',
                    'single_records_kept':      '^FastQ single records kept: (.+?) .+$',
                    'paired_records_discarded': '^FastQ paired records discarded: (.+?) .+$',
                    'single_records_discarded': '^FastQ single records discarded: (.+?) .+$'}
        return {k: int(re.findall(v, self.checker.p.report.contents, re.M)[0]) for k,v in patterns.items()}