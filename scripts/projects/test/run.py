#!/usr/bin/env python2

"""
A script to contain the procedure for running the test sample.
"""

# Built-in modules #

# Internal modules #
import gefes

################################ Preprocessing ################################
proj = gefes.projects['test']
samples = proj.samples
for s in samples:
    s.load()
    s.pair.fwd.fastqc.run()
    s.pair.rev.fastqc.run()
    s.quality_checker.run()
    s.clean.fwd.fastqc.run()
    s.clean.rev.fastqc.run()
    s.clean.fwd.graphs['LengthDist'].plot()
    s.clean.rev.graphs['LengthDist'].plot()
    s.pair.fwd.avg_quality
    s.pair.rev.avg_quality
    s.report.generate()

################################### Assembly ##################################
proj = gefes.projects['test'].load()
proj.runner.run_slurm(steps=[{'assembly41.run':{'threads':False}}], time='00:15:00', qos='short', job_name="test_ray_41", partition='devel')

################################### Aggregate ##################################
a = gefes.groups.favorites.test
a.run_slurm(steps=[{'assembly.run':{}}], threads=False)