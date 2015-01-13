# Built-in modules #

# Internal modules #

# First party modules #
from fasta import FASTA
from plumbing.autopaths import AutoPaths
from plumbing.slurm import num_processors
from plumbing.cache import property_cached

# Third party modules #
import sh

###############################################################################
class Prokka(object):
    """Will run the Prokka software on one single contig.
    http://www.vicbioinformatics.com/software.prokka.shtml
    Expects version 1.10"""

    short_name = 'prokka'
    long_name  = 'Prokka v1.10'
    executable = 'prokka'
    dependencies = ['parallel']

    all_paths= """
    /output/
    /output/prokka_*.txt
    /output/prokka_*.ecn
    /output/prokka_*.err
    /output/prokka_*.faa
    /output/prokka_*.ffn
    /output/prokka_*.fna
    /output/prokka_*.fsa
    /output/prokka_*.gbf
    /output/prokka_*.gff
    /output/prokka_*.log
    /output/prokka_*.sqn
    /output/prokka_*.tbl
    """

    def __init__(self, contig, result_dir):
        # Save Attributes #
        self.contig = contig
        self.result_dir = result_dir
        # Auto paths #
        self.base_dir = self.result_dir + self.short_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def run(self):
        sh.prokka('--outdir', self.p.output,
                  '--cpus', num_processors,
                  '--locustag', 'prokka',
                  '--compliant',
                  '--usegenus',
                  '--metagenome',
                  '--addgene',
                  '--quiet',
                  '--force',
                  self.contig.fasta)

    @property_cached
    def results(self):
        results = ProkkaResults(self)
        if not results: raise Exception("You can't access results from Prokka before running the annotation.")
        return results

###############################################################################
class ProkkaResults(object):

    def __nonzero__(self): return self.prokka.p.log.exists
    def __init__(self, prokka):
        self.prokka = prokka

    @property_cached
    def functions(self):
        """Returns a list of predicted functions, one per predicted protein."""
        return [p.description for p in FASTA(self.prokka.p.faa)]

    @property_cached
    def species(self):
        """Returns the predicted species of this contig."""
        return [p.description for p in FASTA(self.prokka.p.fsa)][0]