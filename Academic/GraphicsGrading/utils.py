from __future__ import annotations
########## INIT ####################################################################################

##### Imports #############################################################
### Standard ###
import time, json, os
now = time.time
from os import environ
from collections import deque

import numpy as np



########## CONFIG HELPERS ##########################################################################

def env_get( varName ):
    """ Get value from env """

    def recur( keyLst, dct ):
        if len( keyLst ) > 1:
            if keyLst[0] in dct:
                return recur( dct[ keyLst[0] ], keyLst[1:] )
            else:
                return None
        else:
            if keyLst[0] in dct:
                return dct[ keyLst[0] ]
            else:
                return None

    if isinstance( varName, list ):
        dct = None
        try:
            dct = json.loads( environ[ varName[0] ] )
            return recur( varName[1:], dct )
        except KeyError:
            print( f"There was NO VARIABLE named {varName}!" )
            return None
    else:
        try:
            return json.loads( environ[ varName ] )
        except KeyError:
            print( f"There was NO VARIABLE named {varName}!" )
            return None
        except Exception:
            return environ[ varName ]
    

def env_sto( varName, varValu ):
    """ Store value in env as JSON """
    environ[ varName ] = json.dumps( varValu )


def read_config_into_env( configJSONpath ):
    """ Open the file and read all the names into the environment, Then return the names that were read """
    config = dict()
    rtnNam = list()
    try:
        with open( configJSONpath, 'r' ) as f:
            config = json.load( f )
            if isinstance( config, dict ):
                for k, v in config.items():
                    try:
                        varNam = f"{k}"
                        env_sto( varNam, v )
                        rtnNam.append( varNam )
                    except Exception as e:
                        print( f"Error writing variable {k}-->{v}: {e}" )
            else:
                raise ValueError( f"{configJSONpath} does NOT qualify as a config file!" )
    except Exception as e:
        print( f"Cannot open file: {configJSONpath}" )
    print( f"The following environment variables are available: {rtnNam}" )
    return rtnNam



########## FILE OPERATIONS #########################################################################

def out_line( outFile, outStr ):
    """ Print and write the output with a newline """
    print( outStr )
    outStr += '\n'
    outFile.write( outStr )


def p_executable( path ):
    """ Return True if the file can be run """
    # Author: ssam, https://ubuntuforums.org/showthread.php?t=1457094&s=d79fc51840d2783bb1461f9a049b7e03&p=9138623#post9138623
    return bool( os.access(path, os.X_OK) )



########## CONTAINERS ##############################################################################

def concat_structs( op1, op2 ):
    """ Combine two data structures, recursively """
    if isinstance( op1, list ) and isinstance( op2, (list, deque,) ):
        rtnLst = deque()
        rtnLst.extend( op1 )
        rtnLst.extend( op2 )
        return list( rtnLst )
    elif isinstance( op1, deque ) and isinstance( op2, (list, deque,) ):
        rtnDqu = deque()
        rtnDqu.extend( op1 )
        rtnDqu.extend( op2 )
        return rtnDqu
    elif isinstance( op1, dict ) and isinstance( op2, dict ):
        rtnDct = dict()
        for k1, v1 in op1.items():
            if k1 in op2:
                rtnDct[ k1 ] = concat_structs( v1, op2[ k1 ] )
            else:
                rtnDct[ k1 ] = v1
        for k2, v2 in op1.items():
            if k2 not in rtnDct:
                rtnDct[ k2 ] = v2
        return rtnDct
    else:
        return None


########## STRING ANALYSIS #########################################################################

def levenshtein_search_dist( s1 : str, s2 : str ) -> int:
    """ Get the edit distance between two strings """
    # Author: Salvador Dali, https://stackoverflow.com/a/32558749
    # 1. Trivial cases: One string is empty
    if not len(s1):
        return len(s2)
    if not len(s2):
        return len(s1)
    # 2. This algo assumes second string is at least as long as the first
    if len(s1) > len(s2):
        s1, s2 = s2, s1
    if s1 in s2:
        return 0
    # 3. Compute distance and return
    distances  = range(len(s1) + 1)
    distances_ = None
    for i2, c2 in enumerate(s2):
        distances_ = deque()
        distances_.append( i2+1 )
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
    return distances_.pop() + abs(len(s1)-len(s2)) # HACK


def tokenize( inStr ):
    """ Split `inStr` into tokens we care about """
    inStr    = str( inStr ) + ',' # Terminator hack
    reserved = ['(',')',',',]
    token    = ""
    tokens   = []
    for ch_i in inStr:
        if (ch_i.isspace() or (ch_i in reserved)) and len( token ):
            tokens.append( token )
            token    = ""
        else:
            token += ch_i
    return tokens


def filter_float_tokens( tokens ):
    """ Return a list of only the numeric tokens as floats """
    rtnTkns = list()
    for token in tokens:
        try:
            flt = float( token )
            rtnTkns.append( flt )
        except ValueError:
            pass
    return rtnTkns



########## GEOMETRY ################################################################################

def vec_unit( v ):
    """ Return the unit vector in the direction of `v` """
    mag = np.linalg.norm( v )
    if mag > 0.0:
        return np.array( v ) / mag
    else:
        return v


def angle_between( v1, v2 ):
    """ Returns the angle in radians between vectors 'v1' and 'v2' """
    # Adapted from code by: David Wolever, https://stackoverflow.com/a/13849249
    v1_u  = vec_unit( v1 )
    v2_u  = vec_unit( v2 )
    vvDot = np.clip( np.dot( v1_u, v2_u ), -1.0, 1.0)
    if abs( vvDot ) < 0.00001:
        return np.pi / 2.0
    else:
        return np.arccos( vvDot )



########## PRINT HELPERS ###########################################################################

class TColor:
    """ Terminal Colors """
    # Source: https://stackoverflow.com/a/287944
    HEADER    = '\033[95m'
    OKBLUE    = '\033[94m'
    OKCYAN    = '\033[96m'
    OKGREEN   = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    ENDC      = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


def disp_text_header( titleStr : str, emphasis : int, preNL : int = 0, postNL : int = 0 ):
    """ Make the headers that you like so much """
    emphStr = '#'*int(emphasis)
    newLine = '\n'
    print( f"{newLine*int(preNL) if preNL else ''}{emphStr} {TColor.OKGREEN}{titleStr}{TColor.ENDC} {emphStr}{newLine*int(postNL) if postNL else ''}" )



