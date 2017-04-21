#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2017-04-16

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
FILENAME.py , Built on Wing 101 for Python 2.7
James Watson, YYYY MONTHNAME
A ONE LINE DESCRIPTION OF THE FILE

Dependencies: numpy
"""

# == Init Environment ======================================================================================================================
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
import __builtin__ # URL, add global vars across modules: http://stackoverflow.com/a/15959638/893511
__builtin__.EPSILON = 1e-7
__builtin__.infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
__builtin__.endl = os.linesep

# ~~ Script Signature ~~
__progname__ = "PROGRAM NAME"
__version__  = "YYYY.MM.DD"
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# == End Init ==============================================================================================================================


# == Main Application ======================================================================================================================

# = Program Vars =



# = End Vars =

if __name__ == "__main__":
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    

# == End Main ==============================================================================================================================


# == Spare Parts ==



# == End Spare ==