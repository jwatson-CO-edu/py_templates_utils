#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

__progname__ = "show_me_what_you_got.py"
__version__  = "2018.06" 
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 2.7

Randomly display the lab updates in their appropriate apps

Dependencies: numpy
"""


"""  
~~~ Developmnent Plan ~~~
[ ] ITEM1
[ ] ITEM2
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
# ~~ Path Utilities ~~
def prepend_dir_to_path( pathName ): sys.path.insert( 0 , pathName ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
from os import listdir
from os.path import isfile, join
from random import shuffle
import subprocess, os
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = Program Functions =

def get_ext( fName ): 
    """ Return the file extension of a file, including the '.' , otherwise return an empty string if there is no '.' """
    # NOTE: everything after the last '.' is assumed to be the extension
    if '.' in fName: 
        ext = ""
        i = -1
        while( fName[i] != '.' ):
            ext = fName[i] + ext
            i -= 1
        return ( "." + ext ).lower()
    else:
        return ''

# _ End Func _

# = Program Vars =

_ALLOWED_EXT = [ '.pptx' , '.ppt' , '.pdf' ]

# _ End Vars _

if __name__ == "__main__":
    print __prog_signature__()
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    onlyfiles = [ f for f in listdir( SOURCEDIR ) if isfile( join( SOURCEDIR , f ) ) ]
    print "Files: ______ " , onlyfiles
    shuffle( onlyfiles )
    print "Shuffled: ___ " , onlyfiles
    
    presPaths = [ join( SOURCEDIR , fName ) for fName in onlyfiles if ( get_ext( fName ) in _ALLOWED_EXT ) ]
    print "Presentations:" , presPaths
    
    print "Opening files ..."
    
    for path in presPaths:
        
	rwin = raw_input( "Enter to open next ..." )
		
        try:
            print "Attemping to open" , path ,
            
            # URL , Open files in the appropriate application: https://stackoverflow.com/a/435669
            if sys.platform.startswith( 'darwin' ):
                subprocess.call( ('open' ,  path ) )
            elif os.name == 'nt':
                os.startfile( path )
            elif os.name == 'posix':
                subprocess.call( ('xdg-open' , path ) )  
                
            print "\tSUCCESS!"
                
        except:
            print "FAILURE OPENING" , path , "!  Skipping ..."

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
