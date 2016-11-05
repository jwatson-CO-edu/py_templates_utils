#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-09-07

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
imperial-measurements.py , Built on Wing 101 for Python 2.7
James Watson, 2016 November
Working with inches and centimeters for personal projects
"""

# == Init Environment ======================================================================================================================
import sys, os.path
from math import pi , log , floor
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326
# == End Init ==============================================================================================================================
infty = 1e309 

import numpy as np

def log2( n ): return log( n , 2 )

def nearest_2_fraction( decimal , greatestDenom ):
    """ Return the measurment nearest to a given decimal number """
    if log2( greatestDenom ) % 1 != 0: raise ValueError("nearest_2_fraction: Denominator must be a power of 2. Got " + str(greatestDenom))
    if decimal % 1 != 0:
        whole = int( floor( decimal ) ) # Get the whole part
        decimal = decimal % 1 # get the decimal part
        denom = 2 ; btm = 0 ; top =1 ; delta = 
        while denom <= greatestDenom:
            pass # FIXME: START HERE!
    else:
        return decimal
    