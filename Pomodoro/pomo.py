#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2020-02-07

__progname__ = "pomo.py"
__author__   = "James Watson"
__version__  = "2020.05"
__desc__     = "A pomodoro application with customizable durations and sequences"

"""  
~~~ DEV PLAN ~~~
[Y] Duration ~ 2020-05-04: math checks out
[Y] Interval ~ 2020-05-13: Countdown works
[Y] PomSeq ~ 2020-05-13: Properly iterates sequence and repeats
[Y] Loop ~ 2020-05-20: Loops properly
[Y] Sound ~ 2020-05-22: Plays in a separate thread, Blocks if not threaded
[Y] Write to XML ~ 2020-05-25: Write an entire sequence to XML, built from recursive dictionaries
[ ] Read from XML
[ ] Tkinter
    [ ] Load File
    [ ] Save file
[ ] Installed Library
    [ ] Package
    [ ] Post to PyPI
[ ] Send functions to MARCHHARE
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
from time import struct_time , time , sleep
from random import choice
from threading import Thread
# ~~ Special ~~
import numpy as np
from pydub import AudioSegment
from pydub.playback import play
from dicttoxml import dicttoxml
import xmltodict
# ~~ Local ~~
from Timing import Duration , Interval

# ___ End Init _____________________________________________________________________________________________________________________________

# [ ] REPLACE IN MARCHHARE
def lists_as_columns_with_titles( lists , titles = [] , padSpaces = 4 , output = 0 ):
    """ Return a string with each of the 'lists' as columns with the appropriate 'titles' """
    from os import linesep as endl
    longestList = 0
    longestItem = 0
    prntLists   = []
    pad         = padSpaces * ' '
    rtnStr      = ""
    
    assert ( len( titles ) == len( lists ) ) or ( len( titles ) == 0 ) , \
           "Titles " + str( len( titles ) ) + " and lists " + str( len( lists ) ) + " of unequal length."
    
    titleOut = len( titles )
    
    if titleOut:
        for title in titles:
            if len( title ) > longestItem:
                longestList = len( title )
    
    for lst in lists:
        if len( lst ) > longestItem:
            longestList = len( lst )
        prntLists.append( [] )
        for item in lst:
            strItem = str( item )
            prntLists[-1].append( strItem )
            if len( strItem ) > longestItem:
                longestItem = len( strItem )
    if titleOut:
        line = ''
        for title in titles:
            line += title[ : len(pad) + longestItem -1 ].rjust( len( pad ) + longestItem , ' ' )
        if output:  print( line )
        rtnStr += line + endl
    for index in range( longestList ):
        line = ''
        for lst in prntLists:
            if index < len( lst ):
                line += pad + lst[ index ].ljust( longestItem , ' ' )
            else:
                line += pad + longestItem * ' '
        if output:  print( line )
        rtnStr += line + endl
    return rtnStr

# [ ] REPLACE IN MARCHHARE
def list_to_dict( lst , keyStringsOnly = 1 ):
    """ Render a list as a dictionary """
    rtnDct = {}
    for key , val in enumerate( lst ):
        sKey = str( key ) if keyStringsOnly else key
        rtnDct[ sKey ] = val
    return rtnDct

def type_name( obj ):
    """ Return the string name of the `obj`s type """
    return type( obj ).__name__

def dict_to_list( dct , numPrefix = '' ):
    """ Render a dictionary as a list """
    maxDex   = -float('inf')
    indices  = []
    contents = {}
    preLen   = len( numPrefix )
    for key in dct.keys():
        if type_name( key ) == 'str':
            # FIXME START HERE, REMOVE THE PREFIX AND PARSE NUMBER
            pass
        k = int( key )
        indices.append( k )
        maxDex = max( maxDex , k )
        contents[ k ] = dct[ key ]
    indices.sort()
    rtnLst = [ None for i in range( maxDex+1 ) ]
    for i in indices:
        rtnLst[i] = contents[ i ]
    return rtnLst

class PomSeq:
    """ A sequence of `Interval`s for Pomodoro """
    
    def __init__( self , sndDir = "" , fNames = [] , repeat = True , strDices = 1 , fullSndPaths = [] ):
        """ Set up bookkeeping for a sequence of intervals """
        self.sequence = [] # ---------------------- Sequence of `Interval`s
        self.activDex = 0 # ----------------------- Index of the `Interval` currently being tracked
        self.active   = False # ------------------- Flag: T if this sequence is keeping time at all
        self.paused   = False # ------------------- Flag: T if this sequence is paused
        self.loop     = repeat # ------------------ Flag: T if the sequence should repeat after final interval finishes
        self.useSound = bool( sndDir and fNames ) # Flag: T if sound should be used
        self.sndPaths = [] # ---------------------- Paths to the sounds used in this 
        self.sounds   = [] # ---------------------- Actual playable sound files for notices
        self.strDices = strDices # ---------------- Flag: T if dictionaries should ALWAYS have string keys
        # If there was a predetermined list of full sound paths
        if len( fullSndPaths ):
            self.useSound = True
            for path in fullSndPaths:
                self.sndPaths.append( path )
                self.sounds.append( AudioSegment.from_mp3( path ) )
        # If the components of a full path collection were passed
        if bool( sndDir and fNames ):
            for f in fNames:
                path = os.path.join( sndDir , f )
                self.sndPaths.append( path )
                self.sounds.append( AudioSegment.from_mp3( path ) )

    def add_interval( self , obj = None , US = None , w = 0 , d = 0 , h = 0 , m = 0 , s = 0 , name = "" ):
        """ Append an `Intervsal` to the `sequence` """
        if obj != None:
            self.sequence.append( obj )
        else:
            self.sequence.append( Interval( US = US , w = w , d = d , h = h , m = m , s = s , name = name ) )
            
    def crnt_intr( self ):
        """ Return the current interval """
        return self.sequence[ self.activDex % len( self.sequence ) ]
            
    def start( self ):
        """ Start the current `Interval` """
        self.crnt_intr().start()
        self.active = True
        self.paused = False
        
    def pause( self ):
        """ Pause the current `Interval` """
        self.crnt_intr().pause()
        self.active = True
        self.paused = True
        
    def stop( self , reset = True ):
        """ Stop the current `Interval` """
        self.crnt_intr().stop()
        self.active = False
        self.paused = False
        if reset:
            self.activDex = 0
            
    def chime( self ):
        """ Play a notification sound at random """
        play( choice( self.sounds ) )
            
    def check_running( self ):
        """ Check if we are in the middle of this interval, Advance if we have surpassed """
        self.crnt_intr().check_running()
        # If not paused, Then handle individual Intervals
        if not self.paused:
            if not self.crnt_intr().active:
                # If sounds are enabled, Play a notification sound at random, otherwise do nothing
                if self.useSound:                
                    T = Thread( target = self.chime ) # create thread
                    T.start() # Launch created thread
                self.activDex += 1
                if ( not self.loop ) and ( self.activDex >= len( self.sequence ) ):
                    self.stop()
                else:
                    self.crnt_intr().start()
            return self.active
        # If paused, then active
        else:
            return True
        
    def report( self ):
        """ Return an array of dicts representing each interval """
        rtnLst = []
        for iDex , item in enumerate( self.sequence ):
            rtnLst.append( {
                'index'     : iDex        ,
                'name'      : item.name   ,
                'remaining' : item.remSec ,
            } )
        return rtnLst
        
    def __str__( self ):
        """ Return a string representing this sequence """
        indices    = []
        names      = []
        remainders = []
        for iDex , item in enumerate( self.sequence ):
            indices.append( iDex )
            names.append( item.name )
            remainders.append( item.remSec )
        titles = [ '#' , 'Label' , 'Remaining' ]
        
        return lists_as_columns_with_titles( [indices,names,remainders] , titles , padSpaces = 4 , output = 0 )
    
    def to_dict( self ):
        """ Serialize this object """
        seq = {} 
        for i , intrvl in enumerate( self.sequence ):
            key = str(i) if self.strDices else i
            seq[ key ] = intrvl.to_dict()
        return {
            'sequence'     : seq , # ------------------------- Sequence of `Interval`s
            'active_index' : self.activDex , # --------------- Index of the `Interval` currently being tracked
            'active'       : self.active , # ----------------- Flag for if this sequence is keeping time at all
            'paused'       : self.paused , # ----------------- Flag for if this sequence is paused
            'loop_flag'    : self.loop , # ------------------- Flag for if the sequence repeats after final interval finishes
            'use_sound'    : self.useSound , # --------------- Flag for whether sound should be used
            'sound_paths'  : list_to_dict( self.sndPaths ) , # Paths to the sounds used in this 
        }
    
    def to_xml( self , pathName = "pomoSettings.xml" ):
        """ Serialize this object to XML """
        # https://www.tutorialspoint.com/How-to-serialize-Python-dictionary-to-XML
        xml     = dicttoxml( self.to_dict() ) # Serialize
        xmlfile = open( pathName , 'w' )
        xmlfile.write( xml.decode() )
        xmlfile.close()
        
    def from_xml( pathName = "pomoSettings.xml" ):
        """ Deserialize an XML file into a `PomSeq` """
        _DEBUG = 1
        
        obj = None
        
        with open( pathName ) as fd:
            
            # https://docs.python-guide.org/scenarios/xml/
            root = xmltodict.parse( fd.read() )['root']
            
            # 1. Gather sound paths
            Nsounds = len( root['sound_paths'] )
            if Nsounds:
                if _DEBUG:  print "Found" , Nsounds , "sound path(s)"
                
                
            
            obj = PomSeq(
                fNames = [] ,
                repeat = True ,
                strDices = 1 ,
                fullSndPaths = 
            )
        
        return obj
        
        
        
        
        
        
        
        
        self.sequence = [] # ---------------------- Sequence of `Interval`s
        self.activDex = 0 # ----------------------- Index of the `Interval` currently being tracked
        self.active   = False # ------------------- Flag: T if this sequence is keeping time at all
        self.paused   = False # ------------------- Flag: T if this sequence is paused
        self.loop     = repeat # ------------------ Flag: T if the sequence should repeat after final interval finishes
        self.useSound = bool( sndDir and fNames ) # Flag: T if sound should be used
        self.sndPaths = [] # ---------------------- Paths to the sounds used in this 
        self.sounds   = [] # ---------------------- Actual playable sound files for notices
        self.strDices = strDices # ---------------- Flag: T if dictionaries should ALWAYS have string keys
        

class PomoApp:
    """ Main driver for the pomodoro program """
    
    def __init__( self ):
        """ Initialize sequence and set up GUI """

# === Main Program =========================================================================================================================

if __name__ == "__main__":
    print( __progname__  , 'by' , __author__ , ', Version:' , __version__ )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # ~~ Duration Test ~~
    if 0:
        d1 = Duration( w = 0 , d = 100 , h = 100 , m = 100 , s = 100 )
        print( d1.to_list() )
        print( d1 )
    
    # ~~ Interval Test ~~
    
    if 0:
        i1 = Interval( w = 0 , d = 0 , h = 0 , m = 0 , s = 5 )
    
        bgn = time()
        Trun = 40
        
        i1.start()
        while( i1.check_running() ):
            print( i1 )
            sleep( 0.5 )
        
    if 1:
        # ~~ Sequence Test ~~
        prefix = 'Resource/MP3/'
        paths  = [ 'Bell_1.mp3' , 'Bell_2.mp3' , 'Bell_3.mp3' ]
        p1 = PomSeq( sndDir = prefix , fNames = paths , repeat = True )
        p1.add_interval( s = 3.0 , name = "First"  )
        p1.add_interval( s = 3.0 , name = "Second" )
        p1.add_interval( s = 3.0 , name = "Third"  )
        
        p1.to_xml( pathName = "pomoSettings.xml" )
        
        if 0:
            p1.start()
            
            while( p1.check_running() ):
                    print( p1 )
                    sleep( 0.5 )
       
    if 0:
        prefix = 'Resource/MP3/'
        paths  = [ 'Bell_1.mp3' , 'Bell_2.mp3' , 'Bell_3.mp3' ]
        for p in paths:
            # playsound(  )
            sound = AudioSegment.from_mp3( os.path.join( prefix , p ) )
            play( sound )
# ___ End Main _____________________________________________________________________________________________________________________________



