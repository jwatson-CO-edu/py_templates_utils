#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2017-06-18

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""@package FILENAME.py
@brief A_ONE_LINE_DESCRIPTION_OF_THE_FILE

James Watson, YYYY MONTHNAME
Built on Spyder for Python 2.7

Dependencies: numpy
"""

# == Init Environment ========================================================================================================== 140 char ==
import sys, os.path # To make changes to the PATH

def first_valid_dir(dirList):
    """ Return the first valid directory in 'dirList', otherwise return False if no valid directories exist in the list """
    rtnDir = False
    for drctry in dirList:
        if os.path.exists( drctry ):
			rtnDir = drctry 
			break
    return rtnDir
        
def add_first_valid_dir_to_path(dirList):
    """ Add the first valid directory in 'dirList' to the system path """
    # In lieu of actually installing the library, just keep a list of all the places it could be in each environment
    validDir = first_valid_dir(dirList)
    print __file__ , "is attempting to load a path ...",
    if validDir:
        if validDir in sys.path:
            print "Already in sys.path:", validDir
        else:
            sys.path.append( validDir )
            print 'Loaded:', str(validDir)
    else:
        raise ImportError("None of the specified directories were loaded") # Assume that not having this loaded is a bad thing
# List all the places where the research environment could be
add_first_valid_dir_to_path( [ '/media/jwatson/FILEPILE/Python/marchhare' ] )

# ~~ Libraries ~~
# ~ Standard Libraries ~
# ~ Special Libraries ~
# ~ Local Libraries ~
from marchhare import * # Load the custom environment, this also loads UCBerkeleyUtil

# Source names must be set AFTER imports!
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
SOURCENAM = os.path.split( __file__ )[1]

def rel_to_abs_path( relativePath ):
    """ Return an absolute path , given the 'relativePath' """
    return os.path.join( SOURCEDIR , relativePath )

# ~~ Script Signature ~~
__progname__ = "PROGRAM NAME"
__version__  = "YYYY.MM.DD"
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# == End Init ================================================================================================================== 140 char ==


# == Main Application ======================================================================================================================

# = Program Vars =



# = End Vars =

if __name__ == "__main__":
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    

# == End Main ==============================================================================================================================


# == Spare Parts ==



# == End Spare ==
