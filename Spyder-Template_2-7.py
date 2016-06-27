#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-06-25

"""
FILENAME.py , Built on Spyder for Python 2.7
James Watson, YYYY MONTHNAME
A ONE LINE DESCRIPTION OF THE FILE
"""

# == Init Environment ==================================================================================================
import sys, os.path
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326

def add_first_valid_dir_to_path(dirList):
    """ Add the first valid directory in 'dirList' to the system path """
    # In lieu of actually installing the library, just keep a list of all the places it could be in each environment
    loadedOne = False
    for drctry in dirList:
        if os.path.exists( drctry ):
            loadedOne = True
            if not drctry in sys.path:
                sys.path.append( drctry )
                print 'Loaded', str(drctry)
            else:
                print str(drctry) , 'was already in the path'
            break
    if not loadedOne:
        print "None of the specified directories were loaded"
# List all the places where the research environment could be
add_first_valid_dir_to_path( [ '/home/jwatson/regrasp_planning/researchenv',
                               '/media/jwatson/FILEPILE/Python/ResearchEnv' ] )
from ResearchEnv import * # Load the custom environment

localize(__file__) # You can now load local modules!

# == End Init ==========================================================================================================