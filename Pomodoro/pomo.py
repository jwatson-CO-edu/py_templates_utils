#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2020-02-07

__progname__ = "pomo.py"
__author__   = "James Watson"
__version__  = "YYYY.MM"
__desc__     = "A_ONE_LINE_DESCRIPTION_OF_THE_FILE"

"""  
~~~ DEV PLAN ~~~
[ ] Duration
[ ] Interval
[ ] PomSeq
[ ] Sound
[ ] Loop
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
sys.path.insert( 0 , PARENTDIR ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt , floor
from time import struct_time
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ___ End Init _____________________________________________________________________________________________________________________________

class Duration( struct_time ):
    """ Model a duration of up to a week """
    
    div = { 'w' : 60 * 60 * 24 * 7,
            'd' : 60 * 60 * 24,
            'h' : 60 * 60,
            'm' : 60 ,
            's' : 1  }
    seq = [ 'w' , 'd' , 'h' , 'm' , 's' ]
    
    def normalize_US( self ):
        """ Set the denominations from the Underlying Seconds """
        totS = self.US
        for tDiv in Duration.seq:
            sDiv = Duration.div[ tDiv ]
            if tDiv != 's':
                setattr( self , tDiv ,  int( floor( totS / sDiv ) )  )
                totS = totS % sDiv
            else:
                setattr( self , tDiv ,  totS  )
                
    def accumulate_US( self ):
        """ Set the Underlying Seconds from the Denominations """
        self.US = 0
        for tDiv in Duration.seq:
            sDiv = Duration.div[ tDiv ]
            self.US += getattr( self , tDiv ) * Duration.div[ tDiv ]
    
    def from_list( self , timeList ):
        """ Parse a list as a duration """
        tLen = len( timeList )
        if tLen > 5:
            raise ValueError( "Input format is list " + str( Duration.seq ) +
                              " from most significant to seconds!" )
        seqSlice = Duration.seq[ -tLen : ]
        
        self.US = 0
        for tDex , tDiv in enumerate( seqSlice ):
            self.US += Duration.div[ tDiv ] * timeList[ tDex ]
        self.normalize_US()
            
    def to_list( self ):
        """ Convert to a list """
        bgnDex = 0
        for bDex , tDiv in enumerate( Duration.seq ):
            bgnDex = bDex
            if getattr( self , tDiv ) != 0:
                break
        seqSlice = Duration.seq[ bgnDex : ]
        rtnList  = []
        for tDiv in seqSlice:
            rtnList.append( getattr( self , tDiv ) )
        return rtnList
            
    
    def __init__( self , US = None , w = 0 , d = 0 , h = 0 , m = 0 , s = 0 ):
        """ Init denominations """
        # Time Math
        # self.divSeq = [ 'w' , 's' , 'm' , 'h' , 'd' ] # Sequence of divisiors
        self.w      = w # Weeks
        self.d      = d # Days
        self.h      = h # Hours
        self.m      = m # Minutes
        self.s      = s # Seconds (Can be fractional)
        self.US     = 0 # Underlying Seconds
        if U
        self.accumulate_US()
        self.normalize_US()

class Interval:
    
    def __init__( self ):
        pass

# === Main Program =========================================================================================================================

if __name__ == "__main__":
    print( __progname__  , 'by' , __author__ , ', Version:' , __version__ )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    

# ___ End Main _____________________________________________________________________________________________________________________________



