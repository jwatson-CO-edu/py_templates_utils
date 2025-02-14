#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2020-02-07

__progname__ = "PROGRAM_NAME.py"
__author__   = "James Watson"
__version__  = "YYYY.MM"
__desc__     = "A_ONE_LINE_DESCRIPTION_OF_THE_FILE"

"""  
~~~ DEV PLAN ~~~
[ ] ITEM1
[ ] ITEM2
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
sys.path.insert( 0 , PARENTDIR ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Program =========================================================================================================================

if __name__ == "__main__":
    print( __progname__  , 'by' , __author__ , ', Version:' , __version__ )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    

# ___ End Main _____________________________________________________________________________________________________________________________
