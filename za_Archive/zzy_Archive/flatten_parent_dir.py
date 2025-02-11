#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
flatten_parent_dir.py , Built on Wing 101 IDE for Python 2.7
James Watson, 2017 August , Template Version: 2017-08-24
Search all subdirs of the container dir and empty single files into the container dir

Dependencies: numpy
"""

# == Init Environment ======================================================================================================================
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
import shutil
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
import __builtin__ # URL, add global vars across modules: http://stackoverflow.com/a/15959638/893511
__builtin__.EPSILON = 1e-7
__builtin__.infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
__builtin__.endl = os.linesep

# ~~ Script Signature ~~
__progname__ = "Flatten Directory"
__version__  = "2017.08.30"
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# == End Init ==============================================================================================================================


# == Main Application ======================================================================================================================

DISALLOWEDDIRS = [ "Robot Reading Group a" ]

def any_in_list_is_substr( subList , bigStr ):
    """ Return True if any of the strings in 'subList' is a substring of 'bigStr' , Otherwise return False """
    for subStr in subList:
	if subStr in bigStr:
	    return True
    return False

def flatten_directory( searchPath ): 
    """ Find all the singular files under 'searchPath' (recursive) and move them directly to 'searchPath' , undoes organization """
    # Walk the 'searchPath'
    for dirName , subdirList , fileList in os.walk( searchPath ): # for each subdir in 'srchDir', including 'srchDir'
	if not any_in_list_is_substr( DISALLOWEDDIRS , dirName ): # Perform moves only if dir is not blocked
	    for fName in fileList: # for each file in this subdir  
		fullPath = os.path.join( dirName , fName )
		if os.path.isfile( fullPath ):
		    destination = os.path.join( searchPath , fName )
		    print "Moving" , fullPath , "to" , destination
		    try:
			shutil.move( fullPath , destination )
		    except:
			print "Failed to move" , endl , fullPath , endl , "to" , endl , fullPath , "!"

def del_empty_subdirs( searchDir ):
    """ Delete all the empty subdirectories under 'searchDir', URL: http://stackoverflow.com/a/22015788/7186022 """
    for dirpath , _ , _ in os.walk( searchDir, topdown = False ):  # Walk the directory from the bottom up
	if dirpath == searchDir: # Do not attempt to delete the top level
	    break
	try:
	    if len( os.listdir( dirpath ) ) == 0: # If there are no files or subfolders in the directory
		os.rmdir( dirpath )
	    # else , the directory is not empty , do not attempt deletion
	except OSError as ex:
	    print "Rejected" , ex

# = Program Vars =



# = End Vars =

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Flatten
    flatten_directory( SOURCEDIR )
    # 2. Discard Empty 
    del_empty_subdirs( SOURCEDIR )
    
    

# == End Main ==============================================================================================================================


# == Spare Parts ==



# == End Spare ==