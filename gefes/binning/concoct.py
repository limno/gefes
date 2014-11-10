# Built-in modules #

# Internal modules #

# First party modules #
from plumbing.autopaths import AutoPaths
from plumbing.cache import property_cached

# Third party modules #
import pandas, sh

###############################################################################
class Concoct(object):
    """Use CONCOCT at https://github.com/BinPro/CONCOCT
    to bin contigs together.
    """

    short_name = 'concoct'

    all_paths = """
    /output/
    /coverage.tsv
    """

    def __repr__(self): return '<%s object on %s>' % (self.__class__.__name__, self.parent)

    def __init__(self, samples, assembly, result_dir):
        # Save attributes #
        self.samples = samples
        self.assembly = assembly
        self.result_dir = result_dir
        # Auto paths #
        self.base_dir = self.result_dir + self.short_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    @property_cached
    def coverage_matrix(self):
        """A dataframe where each row corresponds to a contig, and each column
        corresponds to a sample. The values are the average coverage for that contig
        in that sample."""
        return pandas.dataframe([s.mapper.results.coverage for s in self.samples])

    def run(self):
        # Create the "coverage file" #
        self.coverage_matrix.to_csv(self.p.coverage, sep='\t')
        # Run the pipeline #
        sh.concoct('--coverage_file', self.p.coverage, '--composition_file', self.assembly.results.contig_fasta, '-b', self.p.output_dir)

    @property_cached
    def results(self):
        results = ConcoctResults(self)
        if not results: raise Exception("You can't access results from ConcoctResults before running the binning.")
        return results

###############################################################################
class ConcoctResults(object):

    all_paths = """
    /output/lorem
    """

    def __nonzero__(self): return 0
    def __init__(self, concoct):
        self.concoct = concoct
        self.p = AutoPaths(self.concoct.base_dir, self.all_paths)

    @property_cached
    def lorem(self):
        pass