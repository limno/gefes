# Built-in modules #
import os, time, getpass

# Internal modules #
from gefes.common.autopaths import FilePath
from gefes.common import split_thousands

# Third party modules #
import matplotlib
from matplotlib import animation

# No need for an X display #
matplotlib.use('Agg', warn=False)

################################################################################
class Graph(object):
    """Base class for all graphs"""

    width = 12.0
    height = 7.0
    bottom = 0.14
    top = 0.93
    left = 0.06
    right = 0.98
    formats = ('pdf',)

    def __init__(self, parent, base_dir=None, short_name=None):
        # Save parent #
        self.parent = parent
        # Base directory #
        if not base_dir: self.base_dir = self.parent.p.graphs_dir
        else: self.base_dir = base_dir
        # Short name #
        if short_name: self.short_name = short_name
        # Paths #
        self.path = FilePath(self.base_dir + self.short_name + '.pdf')
        self.csv_path = self.base_dir + self.short_name + '.csv'
        # Extra #
        self.dev_mode = True

    def save_plot(self, fig, axes, width=12.0, height=7.0, bottom=0.14, top=0.93, left=0.06, right=0.98, sep=()):
        # Attributes or parameters #
        w = width  if width  != None else self.width
        h = height if height != None else self.height
        b = bottom if bottom != None else self.bottom
        t = top    if top    != None else self.top
        l = left   if left   != None else self.left
        r = right  if right  != None else self.right
        # Adjust #
        fig.set_figwidth(w)
        fig.set_figheight(h)
        fig.subplots_adjust(hspace=0.0, bottom=b, top=t, left=l, right=r)
        # Data and source #
        if self.dev_mode:
            fig.text(0.99, 0.98, time.asctime(), horizontalalignment='right')
            job_name = os.environ.get('SLURM_JOB_NAME', 'Unnamed')
            user_msg = 'user: %s, job: %s' % (getpass.getuser(), job_name)
            fig.text(0.01, 0.98, user_msg, horizontalalignment='left')
        # Nice digit grouping #
        if 'x' in sep:
            seperate = lambda x,pos: split_thousands(x)
            axes.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(seperate))
        if 'y' in sep:
            seperate = lambda y,pos: split_thousands(y)
            axes.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(seperate))
        # Check directory exists #
        self.path.make_directory()
        # Save it as different formats #
        for ext in self.formats: fig.savefig(self.path.replace_extension(ext))

    def save_anim(self, fig, animate, init, width=15, height=15, bitrate = 10000, fps = 10):
        fig.set_figwidth(height)
        fig.set_figheight(width)
        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=360, interval=20)
        FFMpegWriter = animation.writers['ffmpeg']
        writer = FFMpegWriter( bitrate= bitrate, fps=fps)
        # Save #
        self.avi_path = self.base_dir + self.short_name + '.avi'
        anim.save(self.avi_path, writer=writer, codec='x264')
