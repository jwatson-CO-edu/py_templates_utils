#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__progname__ = "read_PDF_metadata.py"
__version__  = "2019.05"
__desc__     = "Read PDF titles in a directory"
"""
James Watson , Template Version: 2018-05-14
Built on Wing 101 IDE for Python 3.6

Dependencies: numpy , pdfrw
"""


"""  
~~~ NOTES ~~~
2019-05-29: Based on the file structure of ICRA 2018
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
import shutil
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
# Set search directory for proceedings
SEARCHDIR = "/home/jwatson/ICRA2019/media/files/"
# Set output directory for renamed files
LITOUTDIR = "/home/jwatson/ICRA2019/search_results/"
# Fetch ALL filenames and report
ALLFILES  = [ os.path.join( SEARCHDIR , fName ) for fName in os.listdir( SEARCHDIR ) ]
print( "Located" , len( ALLFILES ) , "files in the search dir!" )

# Turn debug printing on and off
_SHOWDEBUG = 0
_VERBOSE   = 1

# This dictionary is used to abbreviate titles
# ... "Big Jargon": "Abbrev" , ...
REPLACEDICT = {
    "Automated" :     "Auto" ,
    "Objects" :       "Obj" , 
    "Object" :        "Obj" , 
    "Planning" :      "Plan" ,
    "Manipulation" :  "Manip" , 
    "Environmental" : "Env" ,
    "Performance" :   "Perf" ,
    "Optimisation" :  "Opt" , 
    "Optimal" :       "Opt" , 
    "Learning" :      "Learn" , 
    "Collision" :     "Collsn" , 
    "Detection" :     "Detect" ,
    "Assembly" :      "Asm" ,
    "assembly" :      "asm" ,
    "Generation" :    "Gen" ,
    "Exploration" :   "Explor" ,
    "System" :        "Sys" , 
    "Collaborative" : "Collab" , 
    "Prediction" :    "Predict" ,
    "Disassembly" :   "Disasm" , 
    "Efficient" :     "Effic" ,
    "Control" :       "Ctrl" , 
    "Heterogeneous" : "Hetero" ,
    "Programming" :   "Program" ,
    "Assisted" :      "Assist" ,
    "Construction" :  "Constr" ,
    "Uncertain" :     "Uncert" ,
    "Design" :        "Dsgn" ,
    "Parameter" :     "Param" ,
    "Flexible" :      "Flex" ,
    "Engineer" :      "Engnr" , 
    "Iterative" :     "Iter" , 
    "Motion" :        "Motn" ,
    "Robotic" :       "Robot" , 
    "Intelligent" :   "Intelgnt" , 
    "Integrating" :   "Integ" ,
    "Pressure" :      "Press" , 
    "An " :           "" ,
    "A " :            "" ,
    "," :             "" ,
    ":" :             "-" ,
}

# Set a limit on title length in chars, excluding year and first author
TITLECHARLIM = 70

# _ End Vars _

# = Program Functions =

# ~ Results Processing ~

def shorten_title( titleStr ):
    """ Perform all the usual abbreviations for paper titles , limit length to 'TITLECHARLIM' """
    rtnStr = str( titleStr )
    for key , val in REPLACEDICT.items():
        #print( "Look at" , key )
        if key in titleStr:
            #print( "substring found!" )
            rtnStr = rtnStr.replace( key , val )
    if len( rtnStr ) > TITLECHARLIM:
        return rtnStr[:TITLECHARLIM]
    else:
        return rtnStr

def strip_parens( titleStr ):
    """ Remove the parentheses that ICRA added """
    return titleStr[1:-1]

def get_EXT( fName ):
    """ Return the capitalized file extension at the end of a path without the period """
    return os.path.splitext( fName )[-1][1:].upper()


# ======= Search =======

def get_first_author( entryDict ):
    """ Get the last name of the first author """
    return entryDict['authors'].split(',')[0].split(' ')[-1].upper()

# === Field Functions ===

def fetch_title( f ):
    """ Fetch the title of the PDF object """
    return f.Info['/Title']

def fetch_keywords( f ):
    """ Fetch the title of the PDF object """
    if _SHOWDEBUG: print( type( f.Info['/Keywords'] ) )
    return [ elem.upper() for elem in f.Info['/Keywords'] ]

def fetch_all_authors( f ):
    """ Get a string composes of all the authors' last names """
    authors = strip_parens( f.Info['/Author'] ).split(',')
    lastNames = ""
    for author in authors:
        lastNames += ( author.split(' ')[-1] + " " ).upper()
    # print( lastNames )
    return lastNames

# ___ End Field ___

def search_field_for_terms( searches , existing = None ):
    """ Search all the titles for the 'terms' 
        NOTE: This function expects that 'searches' is a list of pair lists with item[0] as the Field Function and item[1] as a list of terms 
        NOTE: item[1] must be a list, even for only one term"""
    # NOTE: This function assumes that 'fieldFunc' takes a 'PdfReader' as an argument and returns a string
    # NOTE: Linear search
    count    = 0
    i_loop   = 0
    if existing:
        results = existing
    else:
        results  = {}
    # for each of the full paths
    for fName in ALLFILES:
        i_loop += 1
        if _SHOWDEBUG: print( "DEBUG: , Processing" , fName , "is a" , get_EXT( fName ) , type( get_EXT( fName ) ) , "file" )
        if 'PDF' == get_EXT( fName ):
            if _SHOWDEBUG: print( "\tDEBUG: FOUND PDF! ..." )
            try:
                f = PdfReader( fName ) # open the file for reading
                # If we have not added this file to the dictionary already
                if f.ID[0] not in results:
                    # for each search term , store metadata if the term matches
                    for search in searches:
                        if _SHOWDEBUG:  print( "search:" , search )
                        fieldFunc = search[0]
                        terms     = search[1]
                        for term in terms:
                            try:
                                if _SHOWDEBUG:  print( "term:" , term )
                                if term.upper() in fieldFunc( f ):
                                    
                                    # Increment counter
                                    count += 1

                                    # Display the hit
                                    if _VERBOSE:
                                        print()                             
                                        print( "Hit" , count , ':' , f.Info['/Title'] )
                                        print( f.Info['/Author'] )
                                        print( f.Info['/Keywords'] )
                                        print()

                                    # Store the hit
                                    results[ f.ID[0] ] = {
                                        'path' :     fName , 
                                        'title' :    strip_parens( f.Info['/Title'] ) , 
                                        'authors' :  strip_parens( f.Info['/Author'] ) , 
                                        'keywords' : strip_parens( f.Info['/Keywords'] ) ,
                                        'year' :     int( f.Info['/CreationDate'][3:7] )
                                    }

                            except Exception as ex:
                                print( "ERROR: Could not find tags for" , fName , '\t' , ex )
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
            except:
                print( "ERROR: Could not extract metadata from" , fName )
        else:
            if _SHOWDEBUG: print( "\tDEBUG: NOT PDF! ..." )
        if _VERBOSE:
            if i_loop % 10 == 0:
                print( '.' , end='' )
    print( count , "files match the terms" )
    return results

# _______ End Search _______

# ~ File Processing ~

def informative_file_name( entryDict ):
    """ Given a search hit from the above, generate a filename with important data , sans EXT """
    return str( entryDict['year'] ) + " _ " + shorten_title( entryDict['title'] ) + " _ " + get_first_author( entryDict )
    
def rename_move_hits( results , outputDir ):
    """ Move all the search hits to the desired directory where they will have meaningful names """
    print( "Renaming files ...." )
    count = 0
    for ID , hit in results.items():
        short = informative_file_name( hit )    
        outPath = os.path.join( outputDir , short + ".pdf" )
        shutil.copy( hit['path'] , outPath )
        print( hit['path'] , "--cp->" , outPath )
        count += 1
    print( "Completed" , count , "copy operations!" )

def ensure_dir( dirName ):
    """ Create the directory if it does not exist """
    if not os.path.exists( dirName ):
        os.makedirs( dirName )
    
# _ End Func _

if __name__ == "__main__":
    print( __prog_signature__() )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    if _SHOWDEBUG:
        x = PdfReader( "/media/jwatson/IEEE RAS/media/files/0007.pdf" )
        print( x.keys() )
        print( x.Info )
        print( x.ID )
        print( x.ID[0] == x.ID[1] )
        print( x.Info['/Title'] )
        print( x.Info['/Author'] )
        print( x.Info['/Keywords'] )
        print()

    # Perform a search and store results
    results = search_field_for_terms( [
        [ fetch_all_authors , [ "Levine" , "Hermans" , "Abbeel" , "Lozano-Pérez" , "Rus" ] ] ,
        [ fetch_title       , [ "Assembl" , "Fail" , "Manufacturing" , "Reinforcement" ]  ] ,
        [ fetch_keywords    , [ "Assembl" , "Fail" , "Manufacturing" , "Reinforcement" ]  ] ,
    ] )
    
    if _SHOWDEBUG:
        for ID , hit in results.items():
            short = shorten_title( hit['title'] )
            print( short , len( hit['title'] ) , "-->" , len( short ) ) 
            print( informative_file_name( hit ) )
            print()
            
    # Copy hits to dir
    ensure_dir( LITOUTDIR ) # Create output dir if not exist
    rename_move_hits( results , LITOUTDIR ) # Rename, move, and ENJOY

# ___ End Main _____________________________________________________________________________________________________________________________


# === Spare Parts ==========================================================================================================================



# ___ End Spare ____________________________________________________________________________________________________________________________
