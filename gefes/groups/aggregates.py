# Futures #
from __future__ import division

# Built-in modules #
import gefes
from gefes.assemble.ray import Ray
from gefes.running.aggregate_runner import AggregateRunner

# Internal modules #
from plumbing.autopaths import AutoPaths

###############################################################################
class Aggregate(object):
    """A arbitrary aggregate of several samples."""

    all_paths = """
    /logs/
    /graphs/
    /assembly/
    /binning/
    """

    def __repr__(self): return '<%s object "%s" with %i samples>' % \
                               (self.__class__.__name__, self.name, len(self))
    def __iter__(self): return iter(self.samples)
    def __len__(self): return len(self.samples)
    def __getitem__(self, key):
        if isinstance(key, basestring): return [c for c in self.children if str(c) == key][0]
        elif isinstance(key, int): return self.children[key]
        elif isinstance(key, slice): return self.children[key]
        else: raise TypeError('key')

    @property
    def first(self): return self.samples[0]

    def run_samples(self, steps=None, **kwargs):
        for s in self.samples: s.runner.run()

    def run_samples_slurm(self, steps=None, **kwargs):
        return [s.run_slurm(steps, **kwargs) for s in self.samples]

    def __init__(self, name, samples, base_dir=None):
        # Attributes #
        self.name = name
        self.samples, self.children = samples, samples
        # Base directory #
        if base_dir == None: self.base_dir = gefes.view_dir + 'aggregates/' + name + '/'
        else: self.base_dir = base_dir
        # Load #
        self.loaded = False

    def load(self):
        # Paths #
        self.p = AutoPaths(self.base_dir, self.all_paths)
        # Assemble #
        self.assembly = Ray(self.samples, self.p.assembly_dir)
        self.assembly41 = Ray(self.samples, self.p.assembly_dir, 41)
        self.assembly51 = Ray(self.samples, self.p.assembly_dir, 51)
        self.assembly61 = Ray(self.samples, self.p.assembly_dir, 61)
        self.assembly71 = Ray(self.samples, self.p.assembly_dir, 71)
        # Runner #
        self.runner = AggregateRunner(self)
        # Assemble #
        #self.mapper = Mapper(self)
        # Binner #
        #self.binner = Binner(self)
        # Annotation #
        #self.phylotyper = Phylotyper(self)
        #self.annotation = Binner(self)
        # Load #
        self.loaded = True
        # For convenience #
        return self