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
from math import pi
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326
# == End Init ==============================================================================================================================

# == Base Conversion ==

def bin_2_dec( binStr ):
    """ Convert a binary string to a decimal integer """
    return int( binStr , 2 )

# == End Bases ==