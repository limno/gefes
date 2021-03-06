# -*- coding: utf-8 -*-

# Built-in modules #
import os

# Internal modules #

# First party modules #
from plumbing.color import Color

# Third party modules #

###############################################################################
class ProjectStatus(object):
    """Prints information about a project. Will tell you up to which
    point the data has been processed."""

    def __init__(self, project):
        self.project = project
        self.proj    = project
        self.samples = project.samples

    steps = ['raw', 'first_qc', 'cleaned', 'second_qc', 'initial_taxa', 'mono_assembly',
             'co_assembly', 'mono_mapping', 'merged_assembly', 'mappings', 'merged_mapping',
             'binning', 'merged_binning', 'check_m', 'prodigal', 'phylophlan', 'pfams',
             'tigrfams']

    steps_disabled = ['prodigal']

    def print_long(self):
        for line in self.status(details=True):  print line,
    def print_short(self):
        for line in self.status(details=False): print line,

    @property
    def header(self):
        """A pretty header for the project."""
        message = "# Project '%s' with %i samples #"
        message = message % (self.proj.name, len(self.samples))
        message = '#' * len(message) + '\n' + message + '\n' + '#' * len(message) + '\n'
        return message

    def status(self, details=False):
        """Full message to be printed on the terminal."""
        # Get and update the terminal length #
        self.rows, self.columns = map(int,os.popen('stty size', 'r').read().split())
        # The header #
        yield unicode('\n' + self.header + '\n')
        # The green or red rectangle to print #
        black_block   = u"███"
        green_block   = Color.grn + black_block + Color.end
        red_block     = Color.red + black_block + Color.end
        bool_to_block = lambda b: green_block if b else red_block
        # Do it #
        for step in self.steps:
            title, detail, outcome = getattr(self, step)
            yield bool_to_block(outcome)*2 + ' ' + title + '\n'
            if details:
                for n,o in detail: yield bool_to_block(o) + ' ' + n + '\n'
                yield '-' * self.columns + '\n'

    #---------------------------------- Steps --------------------------------#
    @property
    def raw(self):
        title    = "The raw files for each of the samples"
        func     = lambda s: bool(s.pair)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def first_qc(self):
        title    = "The first quality control on the raw data"
        func     = lambda s: bool(s.pair.fwd.fastqc)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def cleaned(self):
        title    = "The cleaning of the raw data"
        func     = lambda s: bool(s.quality_checker)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def second_qc(self):
        title    = "The second quality control on the cleaned data"
        func     = lambda s: bool(s.clean.fwd.fastqc)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def initial_taxa(self):
        title    = "The initial taxonomic evaluation with Kraken"
        func     = lambda s: bool(s.kraken)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def mono_assembly(self):
        title    = "The mono assembly with just the sample as input"
        func     = lambda s: bool(s.assembly)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def co_assembly(self):
        title    = "The different co-assemblies just with all samples as input"
        func     = lambda a: bool(a)
        items    = [(n,a) for n,a in self.proj.assemblies.items()]
        outcome  = all(func(a) for n,a in items)
        detail   = ((str(n), func(a)) for n,a in items)
        return title, detail, outcome

    @property
    def mono_mapping(self):
        title    = "The mapping of each sample to their own mono-assembly"
        func     = lambda s: bool(s.mono_mapper.p.coverage)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def merged_assembly(self):
        title    = "The merged assembly with multiple kmer sizes"
        func     = lambda p: bool(p.merged)
        items    = [self.proj]
        outcome  = all(func(x) for x in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def mappings(self):
        title    = "The mappings of each sample to different assemblies"
        func     = lambda m: bool(m.p.coverage)
        items    = [(s,a,m) for s in self.samples for a,m in s.mappers.items()]
        outcome  = all(func(m) for s,a,m in items)
        detail   = (("Map %s to %s:"%(s,a), func(m)) for s,a,m in items)
        return title, detail, outcome

    @property
    def merged_mapping(self):
        title    = "The mappings of each sample to the merged assembly"
        func     = lambda s: bool(s.mapper_merged.p.coverage)
        items    = self.samples
        outcome  = all(func(s) for s in items)
        detail   = ((str(s), func(s)) for s in items)
        return title, detail, outcome

    @property
    def binning(self):
        title    = "The binning of all the contigs in each assembly"
        func     = lambda a: bool(a) and bool(a.results.binner.p.clustering)
        items    = [(n,a) for n,a in self.proj.assemblies.items()]
        outcome  = all(func(a) for n,a in items)
        detail   = ((str(n), func(a)) for n,a in items)
        return title, detail, outcome

    @property
    def merged_binning(self):
        title    = "The binning of the contigs in the merged assembly"
        func     = lambda p: bool(p.merged) and bool(p.merged.results.binner.p.clustering)
        items    = [self.proj]
        outcome  = all(func(x) for x in items)
        detail   = ((str(p), func(p)) for p in items)
        return title, detail, outcome

    @property
    def check_m(self):
        title = "The CheckM run on every merged-assembly bin"
        func  = lambda b: bool(b.evaluation)
        if self.proj.merged and self.proj.merged.results.binner:
            items = self.proj.merged.results.binner.results.bins
        else: items = []
        outcome     = all(func(b) for b in items) if items else False
        detail      = (("Bin number %s" % b, func(b)) for b in items)
        return title, detail, outcome

    @property
    def prodigal(self):
        title   = "The determination of the location and number of proteins (prodigal)"
        func    = lambda c: bool(c.proteins)
        items   = self.proj.merged.results.contigs if self.proj.merged else []
        outcome = all(func(s) for s in items) if items else False
        detail  = [("Detail disabled for contigs", True)]
        return title, detail, outcome

    @property
    def phylophlan(self):
        title = "The determination of the taxonomy of each bin (phylophlan)"
        func  = lambda br: bool(br.taxonomy)
        if self.proj.merged and self.proj.merged.results.binner:
            items = [self.proj.merged.results.binner.results]
        else: items = []
        outcome     = all(func(s) for s in items) if items else False
        detail      = ((str(br), func(br)) for br in items)
        return title, detail, outcome

    @property
    def pfams(self):
        title = "The hmmsearch of all predicted proteins against all of pfam."
        func  = lambda b: bool(b.pfams)
        if self.proj.merged and self.proj.merged.results.binner:
            items = self.proj.merged.results.binner.results.bins
        else: items = []
        outcome     = all(func(b) for b in items) if items else False
        detail      = (("Bin number %s" % b, func(b)) for b in items)
        return title, detail, outcome

    @property
    def tigrfams(self):
        title = "The hmmsearch of all predicted proteins against all of tigrfam."
        func  = lambda b: bool(b.tigrfams)
        if self.proj.merged and self.proj.merged.results.binner:
            items = self.proj.merged.results.binner.results.bins
        else: items = []
        outcome     = all(func(b) for b in items) if items else False
        detail      = (("Bin number %s" % b, func(b)) for b in items)
        return title, detail, outcome
