#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__progname__ = "read_PDF_metadata.py"
__version__  = "2018.11"
__desc__     = "Read PDF titles in a directory"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 3.6

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
import os
# ~~ Special ~~
import numpy as np
# ~~ Local ~~
from pdfrw import PdfReader

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty   = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl    = os.linesep

# ~~ Script Signature ~~
def __prog_signature__(): return __progname__ + " , Version " + __version__ # Return a string representing program name and verions

# ___ End Init _____________________________________________________________________________________________________________________________


# === Main Application =====================================================================================================================

# = Program Vars =

SEARCHDIR = "/media/jwatson/FILEPILE/ICRA_2018/"
ALLFILES  = [ os.path.join( SEARCHDIR , fName ) for fName in os.listdir( SEARCHDIR ) ]
print( "Located" , len( ALLFILES ) , "files in the search dir!" )

# _ End Vars _

# = Program Functions =

def search_titles_for_terms( *terms ):
    """ Search all the titles for the 'terms' """
    # NOTE: Linear search
    count = 0
    for fName in ALLFILES:
        f = PdfReader( fName )
        for term in terms:
            if term in f.Info['/Title']:
                print( f.Info['/Title'] )
                print( f.Info['/Author'] )
                print( f.Info['/Keywords'] )
                print()
                count += 1
    print( count , "files match the terms" )
            

# _ End Func _

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # Open the PDF
    x = PdfReader( "/media/jwatson/FILEPILE/ICRA_2018/0005.pdf" )
    print( x.keys() )
    print( x.Info )
    print( x.Info['/Title'] )
    print( x.Info['/Author'] )
    print( x.Info['/Keywords'] )
    print()
    
    search_titles_for_terms( "assembly" , "Assembly" )
    
    

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
