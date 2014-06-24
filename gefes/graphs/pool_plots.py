# Built-in modules #

# Internal modules #
from gefes.graphs import Graph

# Third party modules #
from matplotlib import pyplot

# Constants #
__all__ = ['CleanLengthDist']

################################################################################
class CleanLengthDist(Graph):
    """The distribution of the reads after the cleaning"""
    short_name = 'clean_length_dist'

    def plot(self):
        # Data #
        counts = self.parent.cleaner.fwd.lengths_counter
        label = "%i%% of reads discarded" % (self.parent.cleaner.ratio_discarded * 100.0)
        # Plot #
        fig = pyplot.figure()
        pyplot.bar(counts.keys(), counts.values(), 1.0, color='gray', align='center', label=label)
        axes = pyplot.gca()
        # Information #
        title = 'Distribution of sequence lengths after cleaning for pool "%s"' % self.parent.long_name
        axes.set_title(title)
        axes.set_xlabel('Number of nucleotides in sequence')
        axes.set_ylabel('Number of sequences with this length')
        axes.xaxis.grid(False)
        axes.legend()
        # Save it #
        self.save_plot(fig, axes, sep=('x'))