#!/usr/bin/env python
# -*- coding: utf-8 -*-

# ~~ Libraries ~~
# ~ Standard Libraries ~
import os
# ~ Special Libraries ~
# ~ Local Libraries ~

# ~~ Constants , Shortcuts , Aliases ~~
import __builtin__ # URL, add global vars across modules: http://stackoverflow.com/a/15959638/893511
__builtin__.EPSILON = 1e-7 # Assume floating point errors below this level
__builtin__.infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
__builtin__.endl = os.linesep # Line separator

def ignore_EXT( extList , maxDepth ):
    """ Return string for ",gitignore" to ignore each of the extensions in 'extList' to 'maxDepth' , List extensions without periods """
    rtnStr = ""
    for ext in extList:
        extTerm = "*." + ext + endl
        for i in xrange( maxDepth + 1 ):
            rtnStr += "*/" * i + extTerm
    return rtnStr

def ignore_pattern( patternList , maxDepth ):
    """ Return string for ",gitignore" to ignore each of the extensions in 'extList' to 'maxDepth' , List extensions without periods """
    rtnStr = ""
    for pttrn in patternList:
        term = "*" + pttrn + "*" + endl
        for i in xrange( maxDepth + 1 ):
            rtnStr += "*/" * i + term
    return rtnStr

def ROS_ws_ignore_template():
    print ignore_EXT( ['*~'] , 6 )[:-1]
    print "build/"
    print "devel/"
    
def MSVS_ignore_template():
    print ignore_EXT( ['*~'] , 6 )[:-1]
    print ignore_EXT( ['obj'] , 6 )[:-1]
    print ignore_EXT( ['tlog'] , 6 )[:-1]
    print ignore_EXT( ['log'] , 6 )[:-1]
    print ignore_EXT( ['idb'] , 6 )[:-1]
    print ignore_EXT( ['pdb'] , 6 )[:-1]
    print ignore_EXT( ['suo'] , 6 )[:-1]

def LaTeX_ignore_template():
    print ignore_EXT( ['*~'] , 6 )[:-1]
    print ignore_EXT( ['aux'] , 6 )[:-1]
    print ignore_EXT( ['log'] , 6 )[:-1]
    print ignore_EXT( ['pdf'] , 6 )[:-1]
    print ignore_EXT( ['gz'] , 6 )[:-1]
    
    
if __name__ == "__main__":
    
    print endl , "=== Catkin WS Ignores ==="
    ROS_ws_ignore_template()
    
    print endl , "=== MS Visual Studio Ignores ==="
    MSVS_ignore_template()    
    
    print endl , "=== LaTex Publications ==="   
    LaTeX_ignore_template()