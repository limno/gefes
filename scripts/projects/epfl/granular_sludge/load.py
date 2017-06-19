#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""
A script to load the basic objects for the granular sludge project.
"""

# Built-in modules #
import shutil

# First party modules #
from plumbing.processes import prll_map
from plumbing.timer import Timer

# Internal modules #
import gefes

# Third party modules #
import sh

#################################### Load #####################################
# Load two projects #
proj1 = gefes.load("~/deploy/gefes/metadata/json/projects/epfl/granular_sludge_1/")
proj2 = gefes.load("~/deploy/gefes/metadata/json/projects/epfl/granular_sludge_2/")
projects = (proj1, proj2)
proj = proj1 + proj2