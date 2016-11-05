#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-09-07

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
FILENAME.py , Built on Wing 101 for Python 2.7
James Watson, YYYY MONTHNAME
A ONE LINE DESCRIPTION OF THE FILE
"""

# == Init Environment ======================================================================================================================
import sys, os.path
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326
# == End Init ==============================================================================================================================

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl = os.linesep
DISPLAYPLACES = 5 # Display 5 decimal places by default