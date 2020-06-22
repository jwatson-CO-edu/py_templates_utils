#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2020-02-07

__progname__ = "mass_cpp_chk.py"
__author__   = "James Watson"
__version__  = "2020.03"
__desc__     = "Rename, Unzip, Reorganize, and Compile (CPP) student work, then report on the results"

"""  
~~~ USAGE ~~~
term> python3 mass_cpp_chk.py -src <ZIP_DIR> -src <GRADING_DIR> -nxp <INT_FILES_EXPECTED, default=0> -vrb <0or1_VERBOSE_OUT, default=0>
* FEATURE: This program assumes that ZIP files are downloaded in the order to be graded ( "Moodle Order" ;P )
* BUGTURE: This program SKIPS zip filenames that begin with a numeral (Avoids repeat re-naming, Watch out for random names like "1300_Timmy")
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
sys.path.insert( 0 , PARENTDIR ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
from math import pi , sqrt
import sys , os , subprocess
from zipfile import ZipFile
from shutil import move
# ~~ Special ~~
import numpy as np
# ~~ Local ~~

# ___ End Init _____________________________________________________________________________________________________________________________

# ~~ Globals ~~

_SRC = ""
_DST = ""
_NXP = 0
_VRB = 0
_RPM = 0
_RP1 = ""
_RP2 = ""
_PRG = ""

_WILDCARD = '*'

# ~~~ Functions ~~~

def ensure_dir( dirName ):
    """ Create the directory if it does not exist """
    if not os.path.exists( dirName ):
        try:
            os.makedirs( dirName )
        except Exception as err:
            print( "ensure_dir: Could not create" , dirName , '\n' , err )

def handle_args( argList ):
    """ Set the source and destination directories """
    global _SRC , _DST , _NXP , _VRB , _RPM , _RP1 , _RP2 , _PRG
    if len( termArgs ) % 2 != 0:
        raise ValueError( "Modifier/Argument mismatch!: There were " + str( len( termArgs ) ) + " arguments!, \nArgs:" +
                           str( termArgs ) )
    for i in [ j*2 for j in range( int( len( termArgs )/2 ) )]:
        if termArgs[i] == "-src":
           _SRC = os.path.join( SOURCEDIR , termArgs[i+1] )
           if not os.path.isdir( _SRC ):
               raise OSError( str( _SRC ) + " IS NOT A DIRECTORY" )
           print( "Set source dir to:" , _SRC )
        elif termArgs[i] == "-dst":
           _DST = os.path.join( SOURCEDIR , termArgs[i+1] )
           ensure_dir( _DST )
           print( "Set destination dir to:" , _DST )
        elif termArgs[i] == "-nxp":
            _NXP = int( termArgs[i+1] )
            print( "There are" , _NXP , "CPP files expected for this assignment" )
        elif termArgs[i] == "-vrb":
            if int( termArgs[i+1] ):
                _VRB = 1
                print( "Verbose execution..." )
            else:
                print( "Quiet execution..." )
                _VRB = 0
        elif termArgs[i] == "-rpm":
            if int( termArgs[i+1] ):
                _RPM = 1
                print( "Attempting `main()` repairs..." )
            else:
                print( "No automated repairs..." )
                _RPM = 0
        elif termArgs[i] == "-rp1":
            if str( termArgs[i+1] ):
                _RP1 = str( termArgs[i+1] )
                print( "Repair Prefix:" , _RP1 )
        elif termArgs[i] == "-rp2":
            if str( termArgs[i+1] ):
                    _RP2 = str( termArgs[i+1] )
                    print( "Repair Prefix:" , _RP2 )
        elif termArgs[i] == "-prg":
            if str( termArgs[i+1] ):
                    _PRG = str( termArgs[i+1] )
                    print( "Using Ruleset:" , _PRG )
        else:
            print( "UNKNOWN FLAG:" , termArgs[i] , ", WITH ARGUMENT:" , termArgs[i+1] )
            
def get_EXT( fName ):
    """ Return the filepath before the extension """
    return os.path.splitext( fName )[1][1:]

def strip_EXT( fName ):
    """ Return the filepath before the extension """
    return os.path.splitext( fName )[0]

def q_is_EXT( fName , ext = "zip" ):
    """ Return True if the filename has the `ext`, otherwise return False """
    return get_EXT( fName ).upper() == ext.upper()

class Tally:
    def __init__( self ):
        self.p = 0
        self.f = 0
    def PASS( self ):
        self.p += 1
    def FAIL( self ):
        self.f += 1
    def report( self ):
        total = self.p + self.f
        print( "Out of" , total , ", PASSED:" , self.p , ", FAILED:" , self.f )

def order_names_by_time( src , ext = "zip" ):
    """ Prepend to filenames such they are in alphanum order by time of download """
    # NOTE: This is so that files can be processed in MOODLE-order 
    
    if _VRB: print( "##### SORT #####\n\n" )
    
    timeDict = {}
    tally    = Tally()
    
    # 1. Get paths to all EXT files in this directory
    for fName in os.listdir( src ):
        # 2. Construct the full path to the zip file
        fPath = os.path.join( src , fName )
        # 3. Determine if this is a zip file
        if  os.path.isfile( fPath )  and  q_is_EXT( fName , ext ) :
            # If this file does not already begin with a leading digit, then nominate to rename
            if not fName[0].isdigit():
                timeDict[ os.path.getmtime( fPath ) ] = ( fName , fPath )
            
    # 4. Sort keys by time
    sortdKeys = sorted( timeDict.keys() )
    
    # 5. Rename files in order of download time
    for i , key in enumerate( sortdKeys ):
        # 6. Generate a new name
        nuName = '{0:02d}'.format(i+1) + '_' + timeDict[ key ][0]
        # 7. Generate a new path
        nuPath = os.path.join( src , nuName )
        
        if _VRB: print( "Renaming" , timeDict[ key ][1] , "--to->\n\t" , nuPath )
        
        # 8. Rename the file
        try:
            os.rename( timeDict[ key ][1] ,
                       nuPath )
            if _VRB: print( "\tSUCCESS!" )
            tally.PASS()
        except:
            if _VRB: print( "\tFAILURE!" )
            tally.FAIL()
            
    if _VRB: tally.report()
    if _VRB: print( "~~~ COMPLETE ~~~\n\n" )

def unzip_all( src , dst ):
    """ Give each ZIP in `src` its own decompressed directory in within `dst` """
    tally = Tally()
    
    if _VRB: print( "##### UNZIP #####\n\n" )
    
    # 1. For each zip file in the source
    for fName in os.listdir( src ):
        # 2. Construct the full path to the zip file
        fPath = os.path.join( src , fName )
        if _VRB: print( "Working on" , fPath , "..." )
        # 3. Construct a destination folder
        dstDir = os.path.join( dst , strip_EXT( fName ) )
        ensure_dir( dst )
        if _VRB: print( "\tSending files to:" , dstDir )
        
        try:
            # 4. Create an unzip object and send to the destination directory
            with ZipFile( fPath , 'r' ) as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall( dstDir )
            if _VRB: print( "SUCCESS!\n" )
            tally.PASS()
        except:
            if _VRB: print( "FAILURE!\n" )
            tally.FAIL()
            
    if _VRB: tally.report()
    if _VRB: print( "~~~ COMPLETE ~~~\n\n" )
    
def flatten_dir_files( rootDir ):
    """ Move all files to the top of `rootDir`, Then delete all subfolders """
    tally = Tally()
    
    # 1. Walk the entire directory from root to leaf
    for ( dirpath , dirs , files ) in os.walk( rootDir , topdown = False ):
        # 2. For each file
        for filename in files:
            # 3. Consruct full paths
            fPath = os.path.join( dirpath , filename )
            dPath = os.path.join( rootDir , filename )
            # 4. If the file exists, then move it
            if os.path.isfile( fPath ):
                try:
                    if _VRB: print( "Moving" , fPath , "--to->\n\t" , dPath )
                    os.rename( fPath , dPath )
                    tally.PASS()
                    if _VRB: print( "\tSuccess!" )
                except:
                    tally.FAIL()
                    if _VRB: print( "\tFailure!" )
        try:
            os.rmdir( dirpath )
            if _VRB: print( "\t\tRemoved" , dirpath )
        except OSError as ex:
            if _VRB: print( "\t\tAttempted to remove" , dirpath , "but:" , ex )
            
    if _VRB: tally.report()
    
def flatten_toplevel_dirs( dst ):
    """ Flatten each directory that is directly below `dst` """
    folders = [ os.path.join( dst , name) for name in os.listdir( dst ) if os.path.isdir( os.path.join( dst , name) ) ]
    for dPath in folders:
        if _VRB: print( "Flatten:" , dPath )
        flatten_dir_files( dPath )
    if _VRB: print( "~~~ COMPLETE ~~~\n\n" )

def line_begins_with_key( line , keys = [ '//' , '/*' ] ):
    """ Return true if the line begins with any of the keys """
    rtnBool = False
    for key in keys:
        if line.strip()[ : (len(key)) ] == key:
            rtnBool = True
            break
    return rtnBool

def has_main( origFName , keys = [ 'main(' , 'main (' , 'int main' ] ):
    """ Return true if file contains the string 'int main' on one line """
    rtnBool = False
    with open( origFName , 'r' ) as orgFile:
        orgLines = orgFile.readlines()
        for line in orgLines:
            for key in keys:
                if ( key in line )  and  ( not line_begins_with_key( line ) ):
                    rtnBool = True
                    break
            if rtnBool:
                break
    return rtnBool

def repair_CPP( orig , fNamePrefix , fNamePstfix ):
    """ Create a file whose contents is `fNamePrefix` , `orig` , `fNamePostfix` in that order, then overwrite `orig` """
    tempName = 'tempFile'
    try:
        with open( tempName , 'w' ) as fTemp:
            with open( orig , 'r' ) as orgFile:
                with open( fNamePrefix , 'r' ) as preFile:
                    with open( fNamePstfix , 'r') as pstFile:
                        preLines = preFile.readlines()
                        orgLines = orgFile.readlines()
                        pstLines = pstFile.readlines()
                        
                        for lineSeq in [ preLines , orgLines , pstLines ]:
                            for line in lineSeq:
                                fTemp.write( line + ( "" if '\n' in line else '\n' ) )
                            fTemp.write( '\n'*3 )
        move( tempName , orig )
        return 1
    except:
        return 0
    
def lines_from_file( fPath ): 
    """ Open the file at 'fPath' , and return lines as a list of strings """
    with open( fPath , 'r' ) as f:
        lines = f.readlines()
    return lines

def strip_endlines_from_lines( lines ):
    """ Remove the endlines from a list of lines read from a file """
    rtnLines = []
    for line in lines:
        currLine = ''
        for char in line:
            if char != '\n' and char != '\r':
                currLine += char
        rtnLines.append( currLine )
    return rtnLines

def strip_comments_from_lines( lines ):
    """ Remove everything after each # """
    rtnLines = []
    for line in lines:
        rtnLines.append( str( line.split( '#' , 1 )[0] ) )
    return rtnLines

def purge_empty_lines( lines ):
    """ Given a list of lines , Remove all lines that are only whitespace """
    rtnLines = []
    for line in lines:
        if ( not line.isspace() ) and ( len( line ) > 0 ):
            rtnLines.append( line )
    return rtnLines

def parse_lines( fPath , parseFunc ):
    """ Parse lines with 'parseFunc' while ignoring Python-style # comments """
    rtnExprs = []
    # 1. Fetch all the lines
    lines = lines_from_file( fPath )
    # 2. Scrub comments from lines
    lines = strip_comments_from_lines( lines )
    # 3. Purge empty lines
    lines = purge_empty_lines( lines )
    # 3.5. Remove newlines
    lines = strip_endlines_from_lines( lines )
    # 4. For each of the remaining lines , Run the parse function and save the results
    for line in lines:
        rtnExprs.append( parseFunc( line ) )
    # 5. Return expressions that are the results of processing the lines
    return rtnExprs

def insert_prefix_dir_at_char( initStr , prefixDir , char = '*' ):
    """ Return a version of `initStr` in which `char` is replaced with a `prefixDir` """
    _DEBUG = 0
    # 1. Fetch chunks
    chunks = []
    accum  = 0
    chunk  = ""
    rtnStr = initStr
    # A. For each character in the string
    for i , char_i in enumerate( initStr ):
        # B. If the character is the prefix wildcard, start accumulating and add the char
        if char_i == char:
            accum = 1
            chunk += char_i
        # C. Else if not the prefix, but still accumulating
        elif accum:
            # D. If the character is whitespace, store chunk if exists and stop accumulating
            if char_i.isspace():
                accum = 0
                if len( chunk ) > 0:
                    chunks.append( chunk )
                    chunk = ""
            # E. Else still accumulating
            else:
                chunk += char_i
    # F. Cleanup
    if len( chunk ) > 0:
        chunks.append( chunk )
        chunk = ""
    # 2. Modify chunks so that the prefix is added
    nuChunks = []
    for chunk in chunks:
        nuStr = chunk[1:] # Trim the wildcard
        nuStr = str( os.path.join( prefixDir , nuStr ) )
        nuChunks.append( nuStr )
        
    # 3. Replace chunks in the original string
    for i in range( len( chunks ) ):
        if _DEBUG:
            print( chunks[i] , nuChunks[i] )
            print( "Found chunk?: " , chunks[i] in rtnStr )
            print( rtnStr )
        rtnStr = rtnStr.replace( chunks[i] , nuChunks[i] , 1 )
        
    # 4. Return
    return rtnStr

def batch_compile( dst ):
    """ Attempt to compile every CPP in `dst` and give a per-folder report """
    # NOTE: This function assumes there is one directory per student, and that all CPP files are at top level
    
    Nchars = 20 # Print this number of characters from the full path as a section heading

    print( "##### COMPILE #####\n\n" )
    
    # 1. Retrieve directories only
    dirList     = os.listdir( dst )
    studentList = []
    for dName in dirList:
        studentPath = os.path.join( dst , dName )
        if os.path.isdir( studentPath ):
            studentList.append( studentPath )
    # 2. Sort the directories and report
    studentList.sort()            
    print( "There are" , len( studentList ) , "students to grade ...\n\n" )
    
    # 2.1. Fetch rules, if they exist
    if _PRG:
        rules = parse_lines( _PRG , str )
    else:
        rules = []
    
    # 3. For each of the student directories
    for studentDir in studentList:
        print( "==== Working on" , studentDir , "... ====" )
        
        # 4. COMPILE
        if _PRG:
            
            print( "\t== Compilation results for" , studentDir[-Nchars:] , "==" )
            
            results = [ rule.replace( _WILDCARD , '' ) + " -->\t" for rule in rules ]
            # 4.A. For each rule
            for iRl , rule in enumerate( rules ):
                # B. Transform rule for this student
                compRule = insert_prefix_dir_at_char( rule , studentDir , char = _WILDCARD )
                # C. Compile
                if _VRB:  print( "Running:" , compRule.split() )
                try:
                    sproc = subprocess.run( compRule.split() , shell=False, check=False, 
                                            stdout=(None if _VRB else subprocess.DEVNULL) , # ------------ If verbosity is False, then
                                            stderr=(subprocess.STDOUT if _VRB else subprocess.DEVNULL) ) # dump all subprocess output to DEVNULL
                except Exception as ex:
                    if _VRB:  print( "\t\t" , rule , " failed with error: " , str( ex )[:25] )
                if sproc.returncode == 0:
                    results[ iRl ] += "Passed!"
                else:
                    results[ iRl ] += "! FAILED !"
                    
            print( "\t__ End" , studentDir[-Nchars:] , " Compilation __\n" )

            print( "\tThere are" , len( rules ) , "tests to run ..." )

            for result in results:
                # 5. Report
                print( "\t\t" + result )
                
            print( "\tThe following files were submitted:" , os.listdir( studentDir ) )
                
        else:
            # 4.B. Get a list of CPP files
            fList = os.listdir( studentDir )
            cppLst = []
            for fName in fList:
                if  ( fName[-4:].upper() == ".cpp".upper() )  and  (fName[0] != '.') :
                    cppPth = os.path.join( studentDir , fName )
                    if os.path.isfile( cppPth ):
                        cppLst.append( cppPth )
            cppLst.sort()
            
            nToComp = len( cppLst )
            
            # 4. For each of the CPP files
            print( "\t== Compilation results for" , studentDir[-Nchars:] , "==" )
            results = [ False for elem in cppLst ]
            for iC , fCPP in enumerate( cppLst ):
                
                results[ iC ] = ""
                # 4.1. Attempt `main` repair
                if _RPM:
                    if not has_main( fCPP ):
                        if repair_CPP( fCPP , _RP1 , _RP2 ):
                            results[ iC ] += "Repaired ... " 
                
                # 5. Compile
                sproc = subprocess.run( [ 'g++' , '-std=c++11' , str( fCPP ) ] , shell=False, check=False, 
                                        stdout=(None if _VRB else subprocess.DEVNULL) , # ------------ If verbosity is False, then
                                        stderr=(subprocess.STDOUT if _VRB else subprocess.DEVNULL) ) # dump all subprocess output to DEVNULL
                if sproc.returncode == 0:
                    results[ iC ] += "Compiled!"
                else:
                    results[ iC ] += "! FAILED !"
            print( "\t__ End" , studentDir[-Nchars:] , " Compilation __\n" )

            print( "\tThere are" , len( cppLst ) , "files to compile ..." )
            if  ( _NXP > 0 )  and  ( nToComp != _NXP )  :
                if nToComp < _NXP:
                    print( "\tWARN:" , _NXP-nToComp , "FILES MISSING!" )
                else:
                    print( "\tNote:" , nToComp-_NXP , "excess files!?!" )

            for iC , fCPP in enumerate( cppLst ):
                # 5. Report
                print( "\t\t" , os.path.split( fCPP )[1] , ':' , end = ' ' )
                print( results[ iC ] )
            
        print( "____ End Record ____\n\n" )
        

# === Main Program =========================================================================================================================

if __name__ == "__main__":
    print( __progname__  , 'by' , __author__ , ', Version:' , __version__ )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 0. Take user input
    handle_args( termArgs )
    
    # 1. Rename in modified/Moodle order
    order_names_by_time( _SRC )
    
    # 2. Unzip files, if needed
    unzip_all( _SRC , _DST )
    
    # 3. Flatten Student Directories
    flatten_toplevel_dirs( _DST )
    
    # 4. Attempt compilation
    batch_compile( _DST )

# ___ End Main _____________________________________________________________________________________________________________________________
