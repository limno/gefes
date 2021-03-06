# Futures #
from __future__ import division

# Built-in modules #
import sys, os
import cStringIO as StringIO

# Internal modules #
import gefes
from gefes.map import graphs

# First party modules #
from plumbing.autopaths import AutoPaths, FilePath
from plumbing.cache import property_cached, property_pickled

# Third party modules #
import sh, pandas

# Constants #
home = os.environ.get('HOME', '~') + '/'

###############################################################################
class Mapper(object):
    """Maps reads from a Sample object back to an Assembly object.
    SAMtools is used to index and sort the result (v1.3).
    PCR Duplicates are subsequently removed using MarkDuplicates (v1.101).
    BEDTools is then used to determine coverage (v2.15.0).

    Names follow this standard:
      * The 'map_s' file is sorted.
      * The 'map_smd' file is sorted and mark duplicated.
      * The 'map_smds' file is sorted, duplicated, and sorted again.
    """

    dependencies = ['samtools', 'genomeCoverageBed']

    all_paths = """
    /map.sam
    /map.bam
    /map_s.bam
    /map_smd.bam
    /map_smds.bam
    /map_smds.bai
    /map_smd.metrics
    /map_smds.coverage
    /statistics.pickle
    /graphs/
    /stdout.txt
    /stderr.txt
    """

    def __repr__(self): return '<%s object on %s to %s>' % \
                        (self.__class__.__name__, self.sample, self.assembly)

    def __nonzero__(self): return bool(self.p.coverage)

    def __init__(self, sample, assembly, result_dir):
        # Save attributes #
        self.sample     = sample
        self.assembly   = assembly
        self.result_dir = result_dir
        # Auto paths #
        self.base_dir = self.result_dir + self.short_name + '/'
        self.p = AutoPaths(self.base_dir, self.all_paths)

    def pre_run(self, verbose=True):
        """Check both type of indexes exist"""
        # BT2 Index #
        if not os.path.exists(self.contigs_fasta + '.1.bt2'):
            if verbose: print "Making bowtie index"; sys.stdout.flush()
            self.contigs_fasta.index_bowtie()
        # FAI Index #
        if not os.path.exists(self.contigs_fasta + '.fai'):
            if verbose: print "Making samtools index"; sys.stdout.flush()
            self.contigs_fasta.index_samtools()

    def post_run(self, cpus=1, verbose=True):
        # Create bam file, then sort it and finally index the bamfile #
        if verbose: print "Launching samtools view..."; sys.stdout.flush()
        sh.samtools('view', '-bt', self.contigs_fasta + '.fai', self.p.map_sam, '-o', self.p.map_bam, '-@', cpus)
        if verbose: print "Launching samtools sort..."; sys.stdout.flush()
        sh.samtools('sort', self.p.map_bam, '-o', self.p.map_s_bam, '--threads', cpus)
        if verbose: print "Launching samtools index..."; sys.stdout.flush()
        sh.samtools('index', self.p.map_s_bam)
        # Remove PCR duplicates #
        if verbose: print "Launching MarkDuplicates..."; sys.stdout.flush()
        self.remove_duplicates(cpus=cpus)
        # Sort and index bam without duplicates #
        if verbose: print "Launching Samtools sort again..."; sys.stdout.flush()
        sh.samtools('sort', self.p.map_smd_bam, '-o', self.p.map_smds_bam, '--threads', cpus)
        if verbose: print "Launching Samtools index again..."; sys.stdout.flush()
        sh.samtools('index', self.p.map_smds_bam)
        # Compute coverage #
        if verbose: print "Launching BEDTools..."
        sh.genomeCoverageBed('-ibam', self.p.map_smds_bam, _out=str(self.p.map_smds_coverage))
        # Clean up the ones we don't need #
        os.remove(self.p.map_sam)
        os.remove(self.p.map_bam)
        os.remove(self.p.map_smd_bam)
        # Message #
        if verbose: print "Done for sample %s." % self.sample

    def remove_duplicates(self, cpus=1):
        """Remove PCR duplicates with MarkDuplicates."""
        # Find the jar file #
        current_module = FilePath(gefes.repos_dir + 'bin/MarkDuplicates.jar')
        absolute_path  = FilePath(home + 'repos/gefes/bin/MarkDuplicates.jar')
        path = current_module if current_module.exists else absolute_path
        # Estimate size #
        mem_size = "20"
        # Run the command #
        sh.java('-Xmx%sg' % mem_size,
                '-XX:ParallelGCThreads=%s' % cpus,
                '-XX:+CMSClassUnloadingEnabled',
                '-jar', path,
                'INPUT=%s' % self.p.map_s_bam,
                'OUTPUT=%s' % self.p.map_smd_bam,
                'METRICS_FILE=%s' % self.p.map_smd_metrics,
                'AS=TRUE',
                'VALIDATION_STRINGENCY=LENIENT',
                'MAX_FILE_HANDLES_FOR_READ_ENDS_MAP=1000',
                'REMOVE_DUPLICATES=TRUE')

    #-------------------------------- Shortcuts -----------------------------#
    @property
    def contigs_fasta(self):
        """Convenience shortcut. The filtered contigs of the assembly."""
        return self.assembly.results.contigs_fasta

###############################################################################
class MapperResults(object):

    def __nonzero__(self): return bool(self.p.coverage)
    def __init__(self, mapper):
        self.mapper = mapper
        self.assembly = mapper.assembly
        self.p = mapper.p

    @property_cached
    def mapping_stats(self):
        """The raw number of reads that mapped in every contig. Dict with contig names as keys.
        NB: Unmapped reads that have a mate mapped are assigned to the same chromosome.
        Unmapped reads with no mate or an unmapped mate are assigned to chrom `*`."""
        # Get text output from samtools #
        result = sh.samtools('idxstats', self.p.map_smds_bam)
        result = StringIO.StringIO(result.stdout)
        # Parse result #
        names = ['length', 'mapped', 'unmapped']
        frame = pandas.read_csv(result, sep='\t', index_col=0, names=names)
        frame = frame.drop('length', axis=1)
        return frame

    @property_cached
    def raw_contig_counts(self):
        """The raw number of reads that mapped in every contig.
        #TODO check that this is the number of mapped reads and not the number
        of mapping alignments!"""
        frame = self.mapping_stats.drop('*')
        frame = frame['mapped']
        return dict(frame)

    @property_cached
    def filtered_count(self):
        """The number of reads that we tried to map after removing duplicates.
        Same as: return int(sh.samtools('view', '-c', self.p.map_smds_bam))"""
        return self.mapping_stats.sum().sum()

    @property_cached
    def raw_mapped(self):
        """The raw count of sequences that successfully mapped.
        Same as: return int(sh.samtools('view', '-c', '-F', '4', self.p.map_smds_bam))"""
        return self.mapping_stats['mapped'].sum()

    @property_cached
    def raw_unmapped(self):
        """The raw count of sequences that didn't mapped.
        Same as: return int(sh.samtools('view', '-c', '-f', '4', self.p.map_smds_bam))"""
        return self.mapping_stats['unmapped'].sum()

    @property_cached
    def fraction_mapped(self):
        """The fraction of reads that mapped back to the contigs of the assembly."""
        return self.raw_mapped / self.filtered_count

    @property_cached
    def fraction_unmapped(self):
        """The fraction of reads that did not mapped back to the contigs of the assembly."""
        return self.raw_unmapped / self.filtered_count

    @property_pickled
    def statistics(self):
        """Uses the BEDTools genomeCoverageBed histogram output to determine mean
        coverage and percentage covered for each contig. Returns a dict with contig names as
        keys and containing 'percent_covered' with 'cov_mean' information inside.
        http://bedtools.readthedocs.org/en/latest/content/tools/genomecov.html"""
        print "Computing mapping statistics for sample '%s'" % self.mapper.sample.name; sys.stdout.flush()
        headers = ['name', 'depth', 'count', 'length', 'fraction']
        frame = pandas.io.parsers.read_csv(self.p.map_smds_coverage, sep='\t', index_col=0, names=headers)
        out_dict = {}
        for contig in self.assembly.results.contigs:
            if contig.name not in frame.index:
                cov_mean = 0.0
                percent_covered = 0.0
            else:
                subframe = frame.loc[contig.name]
                assert round(subframe['fraction'].sum(), 4) == 1.0
                cov_mean = (subframe['depth'] * subframe['fraction']).sum()
                not_covered = subframe['depth'] == 0
                if not_covered.any(): percent_covered = float(100 - subframe.loc[not_covered]['fraction'])
                else:                 percent_covered = 100.0
            out_dict[contig.name] = {"cov_mean": cov_mean, "percent_covered": percent_covered}
        return out_dict

    @property_cached
    def coverage_mean(self):
        """The percentage covered in every contig. Dict with contig names as keys"""
        return {contig.name: self.statistics[contig.name]['cov_mean'] for contig in self.assembly.results.contigs}

    @property_cached
    def covered_fraction(self):
        """The mean coverage in every contig. Dict with contig names as keys"""
        return {contig.name: self.statistics[contig.name]['percent_covered'] for contig in self.assembly.results.contigs}

    @property_cached
    def graphs(self):
        class Graphs(object): pass
        result = Graphs()
        for graph in graphs.__all__:
            cls = getattr(graphs, graph)
            setattr(result, cls.short_name, cls(self))
        return result

    @property_cached
    def mean_coverage_graph(self):
        graph = self.graphs.mean_coverage
        if not graph: graph.plot()
        return graph

    @property_cached
    def percent_covered_graph(self):
        graph = self.graphs.percent_covered
        if not graph: graph.plot()
        return graph
