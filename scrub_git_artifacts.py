#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-09-05

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
scrub_git-artifacts.py , Built on Spyder for Python 2.7
2016 November
Get rid of those HEAD notes that Git leaves in files when it has problems with a merge
WARNING: Does not remove the repeat lines that Git sometimes leaves
"""

# == Init Environment ========================================================================================================== 140 char ==
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
SOURCENAM = os.path.split( __file__ )[1]

# ~~ Libraries ~~
# ~ Standard Libraries ~
import datetime , shutil # for timestamps , for file copy
# ~ Special Libraries ~
# ~ Local Libraries ~

# == End Init ================================================================================================================== 140 char ==

def get_ext( fName ): # NOTE: everything after the last '.' is assumed to be the extension
    """ Return the file extension of a file, including the '.' , otherwise return an empty string if there is no '.' """
    if '.' in fName: 
        ext = ""
        i = -1
        while( fName[i] != '.' ):
            ext = fName[i] + ext
            i -= 1
        return "." + ext
    else:
        return ''
        
def lines_from_file( fPath ): 
    """ Open the file at 'fPath' , and return lines as a list of strings """
    f = file( fPath , 'r' )
    lines = f.readlines()
    f.close()
    return lines

def txt_file_for_w( fPath ): 
    """ Open a text file at 'fPath' for writing and return a refernce to the file """    
    return file( fPath , 'w' )
    
def file_from_lines( fPath , lines ):
    """ Write a list of lines into a file at 'fPath' """ 
    # NOTE: This function assumes that each line of 'lines' has a proper newline char if it needs it
    f = txt_file_for_w( fPath )
    f.writelines( lines )
    f.close()
    
nowTimeStamp = lambda: datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') # http://stackoverflow.com/a/5215012/893511
""" Return a formatted timestamp string, useful for logging and debugging """

def bkup_file_name( postfix , fName ):
    """ Return a version of 'fName' with a 'postfix' and timestamp added before the extension """
    ext = get_ext( fName )
    return fName[ : -len(ext) ] + postfix + "_" + nowTimeStamp() + ext

if __name__ == "__main__":
    
    BADPATTERNS = [ "<<<<<<< HEAD" , "=======" , ">>>>>>> " ] # If a line BEGINS with any of these, scrub the line from the file
    TYPESTOCHCK = [ ".py" , ".PY" , ".txt" , ".TXT" , ".csv" , ".CSV" ] # File extenstions that will be corrected
    CORRUPTFDIR = os.path.join( SOURCEDIR , "git_corrupted" ) # Place to back up files before messing with them

    for dirName, subdirList, fileList in os.walk( SOURCEDIR ): # for each subdir in 'srchDir', including 'srchDir'
        for fName in fileList: # for each file in this subdir
            if fName != SOURCENAM: # If the file is other than this one
                if get_ext( fName ) in TYPESTOCHCK: # If this is the type of file that we will consider
                    fPath = os.path.join( dirName , fName )
                    fileCorrupted = False
                    print "Working on:" , fName , "\t" , 
                    fLines = lines_from_file( fPath )
                    nLines = []
                    for line in fLines:
                        badLine = False
                        for pattern in BADPATTERNS:
                            if line.find( pattern ) == 0:
                                badLine = True
                                fileCorrupted = True
                        if not badLine:
                            nLines.append( line )
                    if fileCorrupted:
                        nuPath = os.path.join( CORRUPTFDIR , bkup_file_name( "git_corrupted" , fName ) )
                        print "Backing up:" , nuPath ,
                        shutil.copy( fPath , nuPath )
                        print "Overwriting:" , fPath ,
                        file_from_lines( fPath , nLines )
                    else:
                        print "File OK"
                    