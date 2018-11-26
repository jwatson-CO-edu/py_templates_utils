#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__progname__ = "read_PDF_metadata.py"
__version__  = "2018.11"
__desc__     = "Read PDF titles in a directory"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 3.6

Dependencies: numpy , pdfrw
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
from pdfrw import PdfReader # https://github.com/pmaupin/pdfrw#usage-model

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

def search_field_for_terms( fieldFunc , *terms , existing = None ):
    """ Search all the titles for the 'terms' """
    # NOTE: This function assumes that 'fieldFunc' takes a 'PdfReader' as an argument and returns a string
    # NOTE: Linear search
    count    = 0
    if existing:
        results = existing
    else:
        results  = {}
    # for each of the full paths
    for fName in ALLFILES:
        f = PdfReader( fName ) # open the file for reading
        # If we have not added this file to the dictionary already
        if f.ID[0] not in results:
            # for each search term , store metadata if the term matches
            for term in terms:
                try:
                    if term in fieldFunc( f ):
                        
                        # Display the hit
                        print( f.Info['/Title'] )
                        print( f.Info['/Author'] )
                        print( f.Info['/Keywords'] )
                        print()
                        
                        # Store the hit
                        results[ f.ID[0] ] = {
                            'path' :     fName , 
                            'title' :    f.Info['/Title'] , 
                            'authors' :  f.Info['/Author'] , 
                            'keywords' : f.Info['/Keywords']
                        }
                        
                        # Increment counter
                        count += 1
                except:
                    pass
    print( count , "files match the terms" )
    return results
            
def fetch_title( f ):
    """ Fetch the title of the PDF object """
    return f.Info['/Title']

def fetch_keywords( f ):
    """ Fetch the title of the PDF object """
    return f.Info['/Keywords']

# _ End Func _

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # Open example PDF
    if 0:
        x = PdfReader( "/media/jwatson/FILEPILE/ICRA_2018/0152.pdf" )
        print( x.keys() )
        print( x.Info )
        print( x.ID )
        print( x.ID[0] == x.ID[1] )
        print( x.Info['/Title'] )
        print( x.Info['/Author'] )
        print( x.Info['/Keywords'] )
        print()
    
    # Perform a search and store results
    results = search_field_for_terms( fetch_title    , "assembly" , "Assembly" )
    results = search_field_for_terms( fetch_keywords , "assembly" , "Assembly" , existing =  results )
    

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
