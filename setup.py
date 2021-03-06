from distutils.core import setup

setup(
      name             = 'gefes',
      version          = '1.0.2',
      description      = 'Genome Extraction From Environmental Sequencing',
      long_description = open('README.md').read(),
      long_description_content_type = 'text/markdown',
      license          = 'Proprietary software, all rights reserved.',
      url              = 'http://github.com/xapple/gefes/',
      author           = 'Lucas Sinclair',
      author_email     = 'lucas.sinclair@me.com',
      classifiers      = ['Topic :: Scientific/Engineering :: Bio-Informatics'],
      requires         = ['plumbing', 'fasta', 'pymarktex', 'seqsearch', 'sh', 'tqdm',
                          'biopython', 'decorator', 'threadpool', 'scipy', 'matplotlib',
                          'pandas', 'tabulate', 'ftputil'],
      packages         = ['gefes',
                          'gefes.annotation',
                          'gefes.assemble',
                          'gefes.binning',
                          'gefes.groups',
                          'gefes.map',
                          'gefes.merged',
                          'gefes.metabolism',
                          'gefes.mock',
                          'gefes.parsing',
                          'gefes.preprocess',
                          'gefes.report',
                          'gefes.running',
                          'gefes.status',
                          'gefes.taxonomy',
                          ],
)