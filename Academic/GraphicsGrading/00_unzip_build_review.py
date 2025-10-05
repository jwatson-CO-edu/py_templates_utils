########## INIT ####################################################################################

##### Imports #####
### Standard ###
import os, subprocess, shutil, json, sys
from time import sleep
from collections import deque
from copy import deepcopy
from datetime import date, datetime
from pprint import pprint
### Special ###
import numpy as np
### Local ###
from utils import read_config_into_env, env_get, out_line

##### Constants #####
_CONFIG_PATH = 'HW_Config.json'



########## HELPER FUNCTIONS ########################################################################

def dig_for_Makefile( drctry ):
    """ WHERE IS THE ASSIGNMENT CODE? """
    # Base Case: Assignment is here
    mkPaths = [path for path in os.listdir( drctry ) if "akefile" in path]
    if len( mkPaths ):
        return drctry
    # Recursive Case: Assignment is in a subfolder
    subsubdirs = [p.path for p in os.scandir( drctry ) if p.is_dir()]
    if not len( subsubdirs ):
        return None
    for ssd in subsubdirs:
        # res = dig_for_Makefile( os.path.join( drctry, ssd ) )
        res = dig_for_Makefile( ssd )
        if res is not None:
            return res
    return None


def modify_makefile_to_disable_PIE( hwDir ):
    """ My lab workstation is STUPID """
    mkPath = [path for path in os.listdir( hwDir ) if (("akefile" in path) and os.path.isfile( os.path.join( hwDir, path ) ))]
    mkPath = os.path.join( hwDir, mkPath[0] )
    modTxt = list()
    with open( mkPath, 'r' ) as mkfl:
        orgTxt = mkfl.readlines()
    for line in orgTxt:
        nuLine = line
        if 'CFLG' in line[:5] and 'no-pie' not in line:
            nuLine = f'{nuLine[:-1]} -no-pie\n'
        if 'gcc' in line[:15] and 'no-pie' not in line:
            nuLine = f'{nuLine[:-1]} -no-pie\n'
        modTxt.append( nuLine )
        
    with open( mkPath, 'w' ) as mkfl:
        mkfl.writelines( modTxt )


def make_clean( hwDir ):
    """ Get rid of Windows crap """
    ruleStr = f"make clean -C '{hwDir}'"
    process = subprocess.Popen( ruleStr, 
                                shell  = True,
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE )
    # wait for the process to terminate
    process.communicate()


def scrape_source( hwDir, pattern ):
    """ Attempt to find the `pattern` in the source at `hwDir` """
    try:
        out = subprocess.check_output( f"grep -n \"{pattern}\" {hwDir}/*.c*", 
                                    stderr  = subprocess.STDOUT,
                                    shell   = True,
                                    timeout = 10 )
        return out.decode()
    except subprocess.CalledProcessError as err:
        print( f"Scrape process crashed out:\n{err}\n" )
        return ''
    except subprocess.TimeoutExpired as err:
        print( f"Scrape process timed out, Many files?:\n{err}\n" )
        return ''


def make_in_dir_from_rule_with_output( hwDir, rule, f ):
    """ Make the rule in the child directory and report results """
    runStudent = True

    try:
        ruleStr = f"make {rule} -C '{hwDir}'"

        process = subprocess.Popen( ruleStr, 
                                    shell  = True,
                                    stdout = subprocess.PIPE, 
                                    stderr = subprocess.PIPE )


        # wait for the process to terminate
        out, err = process.communicate()
        out = out.decode()
        err = err.decode()
        errcode = process.returncode

        out_line( f, f"COMPILE Command:  {ruleStr}" )

        if (errcode == 0):
            out_line( f, f"SUCCESS, Compilation Output:  {out}" )
        else:
            out_line( f, f"FAILURE, COMPILATION ERROR:  {err}\n{out}" )
            runStudent = False

    except Exception as e:
        out_line( f, f"FAILURE, PROCESS ERROR:  {e}" )
        runStudent = False

    return runStudent


def find_executable( drctry ):
    """ Return the first executable encountered in `drctry` """
    mkPaths = [path for path in os.listdir( drctry ) if "akefile" in path]
    rtnPath = None
    if len( mkPaths ):
        mkPath = os.path.join( drctry, mkPaths[0] )
        with open( mkPath, 'r' ) as f:
            lines = f.readlines()
            for line in lines:
                elems = line.split(':')
                if len( elems ) > 1:
                    # print( elems )
                    if (".c.o" not in elems[0]) and (".cpp.o" not in elems[0]) and ("all" not in elems[0]) and (elems[0].split('.')[-1] != 'o') and (elems[0].split('.')[-1] != 'a'):
                        rtnPath = os.path.join( drctry, elems[0] )
                        break
    return rtnPath
        

def find_README( drctry ):
    """ Return the first README encountered in `drctry` """
    rdPaths = [path for path in os.listdir( drctry ) if ("readme" in str( path ).lower())]
    if len( rdPaths ):
        return os.path.join( drctry, rdPaths[0] )
    else:
        return None


def source_and_header_full_paths( drctry ):
    """ Get paths to all {*.c, *.cpp, *.h, *.hpp,} """
    rtnPaths = list()
    extMatch = ['c', 'cpp', 'h', 'hpp',]
    srcPaths = [path for path in os.listdir( drctry )]
    for sPath in srcPaths:
        fPath = os.path.join( drctry, sPath )
        if os.path.isfile( fPath ) and (str(fPath).split('.')[-1].lower() in extMatch):
            rtnPaths.append( fPath )
        elif os.path.isdir( fPath ):
            rtnPaths.extend( source_and_header_full_paths( fPath ) )
    return rtnPaths


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


def count_SLOC_comments( fPath ):
    """ Return code size metrics for this file """
    Nsloc = 0
    Ncmnt = 0
    Nline = 0
    lines = list()
    multi = False
    with open( fPath, 'r' ) as f:
        try:
            lines = f.readlines()
            Nline = len( lines )
        except Exception as e:
            print( f"\nFAILED READ because {e}\n" )
            return None, None, None
        for line in lines:
            if ("//" in line) or ("/*" in line) or ("*/" in line):
                Ncmnt += 1
                if ("/*" in line):
                    multi = True
                if ("*/" in line):
                    multi = False
            elif (not multi) and (len( line.strip() ) >= env_get("_MIN_LIN_CH")):
                Nsloc += 1
    return Nsloc, Ncmnt, Nline


def attempt_normal_scan( fPath ):
    """ Attempt to determine if normals are correctly formed """
    f_NormRd = False
    f_3vrtcs = False
    nrm_i    = None
    pts_i    = [None,None,None,]
    ptDex    = 0
    accept   = np.radians( 10.0 )
    glNorm   = False
    nonUnt   = False
    nFound   = False
    feedback = ""

    print()

    with open( fPath, 'r' ) as f:
        try:
            lines = f.readlines()
        except Exception as e:
            print( f"\nFAILED READ because {e}\n" )
            return None
        for j, line in enumerate( lines ):
            try:
                if "GL_NORMALIZE" in str( line ):
                    glNorm = True
                lnTkns = tokenize( line )
                if ("GL_NORMAL_ARRAY" in lnTkns):
                    nFound = True
                if ("glNormal3d" in lnTkns) or ("glNormal3f" in lnTkns):
                    nFound = True
                    if f_NormRd and (not f_3vrtcs):
                        feedback += f"\tUNFINISHED triangle near line {j+1}"
                    elif f_NormRd and (ptDex > 3):
                        feedback += f"\tSURPLUS points near line {j+1}"
                    f_NormRd = True
                    f_3vrtcs = False
                    nrm_i    = np.array( filter_float_tokens( lnTkns ) )
                    mag_i    = np.linalg.norm( nrm_i )
                    if (mag_i > 1.0) or (mag_i < 0.98):
                        nonUnt = True
                    ptDex    = 0
                elif (("glVertex3d" in lnTkns) or ("glVertex3f" in lnTkns)) and f_NormRd:
                    if ptDex <= 2:
                        pts_i[ ptDex ] = np.array( filter_float_tokens( lnTkns ) )
                    ptDex += 1
                    if ptDex > 2:
                        f_3vrtcs = True
                if f_NormRd and f_3vrtcs:
                    f_NormRd = False
                    f_3vrtcs = False
                    s0       = pts_i[1] - pts_i[0]
                    s1       = pts_i[2] - pts_i[1]
                    print( f"Cross {s0} x {s1}", end =" = ", flush = True )
                    nrm_c = vec_unit( np.cross( s0, s1 ) )
                    print( nrm_c )
                    err_i    = angle_between( nrm_i, nrm_c )
                    if err_i > accept:
                        feedback += f"\n\tBAD NORMAL before line {j+1}, Err = {err_i:.3f} rad, {nrm_i} -vs- {nrm_c}" 
                    else:
                        print( '.', end='', flush=True )
            except Exception as e:
                feedback += f"~Line {j+1}: Norm Parser Fault, {e}"
    if nonUnt and (not glNorm):
        feedback += f"\n\tNon-unit normals *without* GL_NORMALIZE enabled!"
    if not nFound:
        return "No Normals"
    return feedback


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



########## GRADER CLASS TO GRADE THE CLASS #########################################################

class GraphicsInspector:
    """ GRIN: CSCI 4/5229 Grading Utility """

    ##### Init ############################################################

    def get_stored_grading_state( self, fPath ):
        """ Get the local stored state """
        self.state  = None
        self.sPath  = fPath
        self.stdNam = None
        if os.path.isfile( fPath ):
            with open( fPath, 'r' ) as f:
                self.state = json.load( f )
        else:
            self.state = {"lastStudent": env_get("_STATE_INT"),}
        if "evals" not in self.state:
            self.state["evals"] = dict()
        if "resubNames" not in self.state:
            self.state["resubNames"] = list()
        return self.state
    

    def store_student_eval( self, nameKey : str, record : dict ):
        """ Store the student record """
        self.state["evals"][ nameKey ] = deepcopy( record )

    
    def fetch_student_eval( self, nameKey ):
        """ Fetch the student record  if it exists, Otherwise return `None` """
        if nameKey in self.state["evals"]: 
            return deepcopy( self.state["evals"][ nameKey ] )
        else:
            return None  

    def store_grading_state( self ):
        """ Set the local stored state """
        with open( self.sPath, 'w' ) as f:
            json.dump( self.state, f, indent = 2 )


    def get_ordered_students( self, listPath ):
        """ Prep student list for searching """
        self.students : list[list[str]] = list()
        with open( listPath, 'r' ) as f:
            lines = f.readlines()
            for line in lines:
                if len( line ) > 2:
                    self.students.append( line.replace('-','').lower().split() )
        self.students.sort( key = lambda x: x[-1] )
        return self.students


    def __init__( self, configPath ):
        """ Set up the inspector for a grading session """
        read_config_into_env( configPath )
        try:
            self.get_stored_grading_state( env_get("_STATE_PTH") )
        except Exception as e:
            self.state = dict()
            self.sPath = env_get("_STATE_PTH")
        

    


    def shutdown( self ):
        """ Tasks to run on exit """
        self.store_grading_state()
        sleep( 1.5 )
        print( f"\n\n########## Set a new Due Date for the Following Students! ##########\n" )
        for resub in self.state["resubNames"]:
            print( resub )
        print()
        with open( "99_Resubs.txt", 'w' ) as f:
            f.writelines( [f"{item}\n\n" for item in self.state["resubNames"]] )


    ##### File Operations #################################################
    
    def unzip_all( self ):
        """ Unzip all student submissions """
        count    = 0
        zpPaths  = [path for path in os.listdir() if ".zip" in path]        
        zpPaths.sort()

        for zp_i in zpPaths:
            folder = zp_i.split( '.' )[0]
            prefix = self.get_student_prefix( folder )
            
            if (prefix is not None):
                folder = f"{prefix}{folder}"
                if os.path.exists( folder ):
                    print( f"{folder} EXISTS!, Skip unzip ..." )
                    continue
                count += 1
                print( f"About to unpack {zp_i}\n\tto {folder}...", end='' )

                try:
                    shutil.unpack_archive( zp_i, folder )
                    print( "SUCCESS" )
                except Exception as e:
                    print( f"FAILURE: {e}" )

        print( f"Expanded {count} student submissions!" )


    def startup( self ):
        """ Tasks to run before grading """
        self.get_ordered_students( env_get("_LIST_PATH") )
        grin.unzip_all()
        sleep( 1.5 )
        self.subdirs = [ f.path for f in os.scandir() if f.is_dir() ]
        self.subdirs.sort()
        self.reports = list()
        self.N_stdnts = len( self.students )
        os.makedirs( env_get("_BAD_DIR" ), exist_ok = True )
        os.makedirs( env_get("_GOOD_DIR"), exist_ok = True )
        self.rubric   : dict = env_get("_RUBRIC_DCT" )
        self.template : dict = env_get("_SCORING_DCT")


    ##### Grading Helpers #################################################
    idx0 = 0
    # idx1 = 1
    idx1 = -1

    def get_student_prefix( self, query ):
        """ Get a prefix that orders the folders """
        for stdnt in self.students:
            if (stdnt[GraphicsInspector.idx0] in query) and (stdnt[GraphicsInspector.idx1] in query):
                return f"{stdnt[GraphicsInspector.idx1]}_{stdnt[GraphicsInspector.idx0]}_"
        return None
    

    def get_student_dir( self, query ):
        """ Get the folder from the name """
        for i, folder in enumerate( self.subdirs ):
            if self.get_student_prefix( query ) in folder:
                return folder, i
        return None, None


    def get_student_name( self, query ):
        """ Get a prefix that orders the folders """
        for stdnt in self.students:
            if (stdnt[GraphicsInspector.idx0] in query) and (stdnt[GraphicsInspector.idx1] in query):
                first = f"{stdnt[GraphicsInspector.idx0][0].upper()}{stdnt[GraphicsInspector.idx0][1:]}"
                secnd = f"{stdnt[GraphicsInspector.idx1][0].upper()}{stdnt[GraphicsInspector.idx1][1:]}"
                return f"{first} {secnd}"
        return None
    

    ##### Menu Functions ##################################################

    def search_ranked_student_index_in_list( self, searchStr : str, Nrank : int = 5 ) -> list[tuple[str,int,int]]:
        """ Return a list of indices that correspond to the search string, Ranked by Levenshtein edit distance """
        rtnRank = list()
        # 0. Remove initial and trailing space
        searchStr = searchStr.strip()
        # 1. Handle <Last,First> and <First Last> inputs
        dbblSrch  = False
        if ',' in searchStr:
            dbblSrch = True
            parts    = [prt.strip().lower() for prt in searchStr.split(',')]
            lastSrch = parts[0]
            frstSrch = parts[-1]
        elif ' ' in searchStr:
            dbblSrch = True
            parts    = [prt.strip().lower() for prt in searchStr.split(' ')]
            lastSrch = parts[-1]
            frstSrch = parts[0]
        # 2. Rank all students
        for i, student in enumerate( self.students ):
            stdntNm  = self.get_student_name( student )
            lastLowr = student[0].lower()
            frstLowr = student[-1].lower()
            # A. Full Name Search, Ranked by total Levenshtein distance = first + last
            if dbblSrch:
                rtnRank.append( (stdntNm, i, levenshtein_search_dist( lastLowr, lastSrch )+levenshtein_search_dist( frstLowr, frstSrch ), ) )
            # B. Single Name Search, Ranked by min Levenshtein distance across {first,last,}
            else:
                rtnRank.append( (stdntNm, i, min(levenshtein_search_dist( lastLowr, searchStr ),levenshtein_search_dist( frstLowr, searchStr )), ) )
        rtnRank.sort( key = lambda x: x[-1] )
        rtnRank = rtnRank[ 0 : Nrank ]
        disp_text_header( f"{Nrank} Search Results", 1, 1, 0 )
        for i, student in enumerate( rtnRank ):
            print( f"\t{student[0]}, {student[-1]:02}, {i if (i>0) else '*'}" )
        disp_text_header( f"End", 1, 0, 1 )
        return rtnRank


    ##### Grading Helpers #################################################

    def get_timestamp( self ):
        """ Get the filename of today's daily note """
        # Get the current date, Format the date as YYYY-MM-DD
        return f"{date.today().strftime('%Y-%m-%d')}_{datetime.now().strftime('%H-%M-%S')}"


    def truthy_user_response( self, 
                              prompt : str = "\nProvide an answer that can be evaluated as a Boolean, then press [Enter]: "  ):
        """ Return a bool based on a user response """
        got = input( f"{prompt}: " )
        if not len( got ):
            return None
        elif "y" == got.strip().lower():
            return True
        elif "n" == got.strip().lower():
            return False
        else:
            return got

    
    def prompt_comment_bullets( self, topicStr = "COMMENTS" ) -> dict:
        """ Build up a comment in pieces """    
        rtnDct = { topicStr: list() }
        while 1:
            comment = input( f"\nWrite a comment for this student and then press [Enter]: " )
            if len( comment ):
                rtnDct[ topicStr ].append( comment )
            else:
                break
        return rtnDct
        

    def prompt_deduction_bullets( self, topicStr = "DEDUCTIONS" ) -> dict:
        """ Build up a comment in pieces """    
        rtnDct = { topicStr: list() }
        while 1:
            comment = input( f"\nWrite a comment '&' deduction for this student and then press [Enter]: " )
            if len( comment ):
                parts = comment.split('&')
                rtnDct[ topicStr ].append( {
                    "Remark": f"{parts[0]}",
                    "Penalty": int( parts[1] )
                } )
            else:
                break
        return rtnDct
    

    def register_resub( self, name ):
        """ Mark name for resubmit """
        self.state["resubNames"].append( name )
        self.state["resubNames"] = list( set( self.state["resubNames"] ) )
    

    def prompt_resub_bullets( self, rubric ) -> dict:
        """ Build up a comment in pieces """    
        while 1:
            comment = input( f"\nWrite a RESUB concern for this student and then press [Enter]: " )
            if len( comment ):
                rubric["Feedback"]["RESUBMIT"].append( comment )
                self.register_resub( rubric["Name"] )
            else:
                break
        return rubric["Feedback"]["RESUBMIT"]


    ##### Per-Student Reporting ###########################################

    def run_student_report( self, studentStr : str, studentDir : str, carryover : dict = None ):
        """ Get info on student submission and generate a report about it """
        reportPath  = studentStr + ".txt"
        runStudent  = True
        rubric      = deepcopy( self.template )
        self.stdNam = self.get_student_name( studentStr )
        rubric["Name"     ] = self.stdNam 
        rubric["Timestamp"] = self.get_timestamp() 
        if carryover is not None:
            rubric = concat_structs( rubric, carryover )

        def get_rubric_flags( key ):
            """ Get any flags associated with this rubric `key` """
            nonlocal rubric, self
            if (key in self.rubric) and ("Flags" in self.rubric[ key ]):
                return list( self.rubric[ key ]["Flags"] )
            else:
                return list()
            
        def p_rubric_flag( key, flag ):
            """ Does the `key` have this `flag` """
            return (flag in get_rubric_flags( key ))
            
        def get_student_flags():
            """ Get any flags associated with this rubric student """
            nonlocal rubric, self
            if ("Flags" in rubric):
                return list( rubric["Flags"] )
            else:
                return list()
            
        def p_student_flag( flag ):
            """ Does the `key` have this `flag` """
            return (flag in get_student_flags())

        def add_student_flag( nuFlag ):
            nonlocal rubric, self
            if ("Flags" not in rubric):
                rubric["Flags"] = list()
            rubric["Flags"].append( nuFlag )
            rubric["Flags"] = list( set( rubric["Flags"] ) )

        def handle_rubric_item( key, res = None ):
            nonlocal rubric, self
            if key in self.rubric:
                if p_student_flag( "resub" ) and p_rubric_flag( key, "skipOnResub" ):
                    print( f">>> {self.stdNam}: SKIP {key} on resub! >>>" )
                    return None
                prm = f"Evaluate Category, {key}"
                if res is not None:
                    prm += f", Got {res}"
                    if res != self.rubric[ key ]["Correct"]:
                        if p_rubric_flag( key, "Ask" ):
                            ans = self.truthy_user_response( prm )
                            res = ans if (ans is not None) else res
                else:
                    res = self.truthy_user_response( prm )
                if res != self.rubric[ key ]["Correct"]:
                    penalty = True
                    if p_rubric_flag( key, "Resubmit" ):
                        penalty = self.truthy_user_response( f"\nForce penalty for {key}? (Repeat Offense)" )
                        if not penalty:
                            add_student_flag( "resub" )
                            self.register_resub( studentStr )
                            if "Remark" in self.rubric[ key ]:
                                rubric["Feedback"]["RESUBMIT"].append( self.rubric[ key ]["Remark"] )
                            else:
                                rubric["Feedback"]["RESUBMIT"].append( input( f"\nNO remark for {key}: " ) )
                    if penalty:
                        rubric["Feedback"]["DEDUCTIONS"].append( {
                            "Remark": f"{self.rubric[ key ]['Remark']}",
                            "Penalty": int( self.rubric[ key ]['Penalty'] )
                        } )

        with open( reportPath, 'w' ) as f:
            out_line( f, f"########## Student: {self.stdNam} ##########\n\n" )
            out_line( f, f"Hello {self.stdNam}!\nTake note of the compilation errors shown below! (You can ignore make rules not in your Makefile.)\n\n" )
            
            ##### Zip File Depth ################# 
            hwDir = dig_for_Makefile( studentDir )
            depth = str( hwDir ).count('/')
            handle_rubric_item( "Executable Depth", depth )

            if hwDir is not None:
                out_line( f, f"Makefile DEPTH: {depth}\n" )
                out_line( f, f"Makefile is here: {hwDir}\n" )
            else:
                out_line( f, f"FAILURE: NO MAKEFILE IN THIS SUBMISSION\n" )
                runStudent = False
            
            ##### Erase Previous Out Files #######
            make_clean( hwDir )

            ##### Zip File Depth #################
            if "Normal Scan" in self.rubric:
                out_line( f, f"##### Normal Scan for: {self.stdNam} #####\n" )
                srcPaths = [path for path in source_and_header_full_paths( hwDir ) if ((".h" not in path) and (".hpp" not in path))] 
                noNormal = True
                for sPath in srcPaths:
                    normOut = f"\n### Normal Scan for: {str(sPath).split('/')[-1]} ###\n"
                    pathOut = attempt_normal_scan( sPath )
                    if (pathOut != "No Normals"):
                        noNormal = False
                    if len( pathOut ) and (pathOut != "No Normals"):
                        normOut += pathOut
                        rubric["Feedback"]["GEOMETRY"].append( normOut )
                if noNormal:
                    rubric["Feedback"]["GEOMETRY"].append( ">>>>>! NO NORMAL DATA: LIGHTING NOT ATTEMPTED !<<<<<" )
                handle_rubric_item( "Normal Scan" )

            ##### Find and Display README ########
            fRead = find_README( hwDir )
            pRead = None
            if fRead is not None:
                os.system( f"{env_get('_TXT_READER')} {fRead}" )
                print( f"Opened README at {fRead}" )
                pRead = True
            else:
                out_line( f, f"BAD: >>NO<< README provided to the grader!" )
                pRead = False
            handle_rubric_item( "README Present", pRead )

            ##### Source Check (Banned Libs) #####
            if len( env_get("_BAD_PATTRN") ):
                match = scrape_source( hwDir, env_get("_BAD_PATTRN") )
                if len( match ):
                    out_line( f, f"EXAMINE THIS LIST MATCHING \"{env_get('_BAD_PATTRN')}\":\n{match}\n" )
                else:
                    print( f"No prohibited text found!\n" )

            ##### Attempt Compilation ############
            if runStudent:
                if env_get("_ALWAYS_PIE"):
                    modify_makefile_to_disable_PIE( hwDir )
                for rule in env_get("_RULE_NAMES"):
                    runStudent = make_in_dir_from_rule_with_output( hwDir, rule, f )
                    if runStudent:
                        break
            if runStudent:
                out_line( f, f"########## Compilation SUCCESS! ##########\n\n" )
                fExec = find_executable( hwDir )
            else:
                fExec = None
            runStudent = (fExec is not None) and os.path.isfile( fExec )
            handle_rubric_item( "Compiles Without Errors", runStudent )
            
            execName = str(fExec).split('/')[-1]
            handle_rubric_item( "Correct Executable Name", execName )

            if runStudent:
                print( f"Executable NAME: {execName}\n" )
                print( f"Running ./{fExec} ..." )
                os.system( f"./{fExec}" )
            else:
                os.system( f"./{hwDir}/{env_get('_GOOD_NAME')}" )
                out_line( f, f"ERROR: >>NO<< executable found at the expected location!" )
            if not runStudent:
                out_line( f, f"########## NOTIFY Student! ##########\n\n" )

            ##### Comment + AI Checks ############
            out_line( f, f"##### Source Check for: {self.stdNam} #####\n" )
            srcPaths = source_and_header_full_paths( hwDir )
            NcomTot  = 0
            NlinTot  = 0
            NlinMax  = 0
            pathMax  = None
            for sPath in srcPaths:
                Nsloc, Ncmnt, Nline = count_SLOC_comments( sPath )
                NcomTot += Ncmnt
                NlinTot += Nline
                if Nsloc > NlinMax:
                    NlinMax = Nsloc
                    pathMax = sPath
            if pathMax is not None:
                os.system( f"{env_get('_TXT_READER')} {pathMax}" )
            else:
                raise ValueError( f"NO SOURCE found for {studentStr}" )

            ##### Per-Assignment Eval Categories #
            for cat in [item for item in self.rubric.keys() if item[:2] == "PA"]:
                handle_rubric_item( cat )
            for cat in ["Contains GenAI Output", "Name in Window Title", "Distort on Resize",]:
                handle_rubric_item( cat )

            ##### Prompt Final Comments ##########
            rubric["Feedback"] = concat_structs( rubric["Feedback"], self.prompt_comment_bullets()   )
            rubric["Feedback"] = concat_structs( rubric["Feedback"], self.prompt_deduction_bullets() )
            self.prompt_resub_bullets( rubric )

            ##### Nudge Secretive Students #######
            if ((NcomTot / NlinTot) < env_get("_L_COM_FRAC")):
                rubric["Feedback"]["COMMENTS"].append( "For future assignments, if you could add some comments to explain your approach in broad terms, it would help us a great deal." )

            ##### Compute Final Score ############
            print( "##### PASTE THESE COMMENTS #####" )
            print( f"{TColor.BOLD}{TColor.OKCYAN}", end="", flush=True )
            if len( rubric["Feedback"]["RESUBMIT"] ):
                print( "##### RESUBMIT #####" )
                for item in rubric["Feedback"]["RESUBMIT"]:
                    print( f"* {item}" )
            if len( rubric["Feedback"]["COMMENTS"] ):
                print( "##### COMMENTS #####" )
                for item in rubric["Feedback"]["COMMENTS"]:
                    print( f"* {item}" )
            if len( rubric["Feedback"]["DEDUCTIONS"] ):
                print( "##### DEDUCTIONS #####" )
                for item in rubric["Feedback"]["DEDUCTIONS"]:
                    print( f"* {item['Remark']}, {item['Penalty']}" )
                    rubric["Student Score"] += item["Penalty"]
            if len( rubric["Feedback"]["GEOMETRY"] ):
                print( "##### GEOMETRY #####" )
                for item in rubric["Feedback"]["GEOMETRY"]:
                    print( f"{item}" )
            print( TColor.ENDC, end="", flush=True )
            print( "##### END PASTE #####" )
            out_line( f, f"\n{self.stdNam} final score: {rubric['Student Score']}\n\n" )
            out_line( f, f"\n{self.stdNam} eval COMPLETE!\n\n" ) 

            # self.store_student_eval( self.stdNam, rubric )
            self.store_student_eval( studentStr, rubric )

        if runStudent:
            shutil.move( reportPath, os.path.join( env_get("_GOOD_DIR"), reportPath ) )
        else:
            shutil.move( reportPath, os.path.join( env_get("_BAD_DIR") , reportPath ) )

        
    def run_menu( self ):
        """ Handle user input, per iteration """
        usrCmd = input( "Press [Enter] to evaluate the next student: " ).upper()
        print()
        rtnState = {
            'loop'   : "",
            'iDelta' :  0 ,
            'index'  : -1 ,
            'reverse': False,
            'flags'  : [],
        }
        ## Handle user input ##
        # Normal List Progression #
        if not len( usrCmd ):
            rtnState['iDelta'] = 1
        # GOTO Student in Current List #
        elif ('S' in usrCmd.upper()):
            if (':' in usrCmd):
                searchStr = usrCmd.split(':')[-1].strip().lower()
            elif (',' in usrCmd):
                searchStr = usrCmd.split(',')[-1].strip().lower()
            else:
                searchStr = usrCmd.split(' ')[-1].strip().lower()
            print( f"Search for {searchStr} ..." )
            ranking = self.search_ranked_student_index_in_list( searchStr, Nrank = env_get("_N_SEARCH_R") )
            invalid = True
            while invalid:
                srchCmd = input( "Press [Enter] to accept top hit or enter number of desired result, Cancel with 'c': " ).upper()
                if len( srchCmd ):
                    try: 
                        rnkChoice = int( srchCmd )
                        invalid   = False
                    except Exception as e:
                        if srchCmd == 'Q':
                            disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
                            sys.exit(0)
                        elif srchCmd == 'C':
                            rnkChoice = -1
                            invalid   = False
                        else:
                            print( f"{srchCmd} was not a choice, Try again, {e}" )
                else:
                    rnkChoice = 0
                    invalid   = False
            if rnkChoice >= 0:
                print( f"Return item {ranking[rnkChoice]} at index {ranking[rnkChoice][1]}" )
                rtnState['index'] = ranking[rnkChoice][1]
            rtnState['loop'] = "continue"
        # Quit #
        elif 'Q' in usrCmd:
            disp_text_header( f"END PROGRAM", 10, preNL = 2, postNL = 1 )
            sys.exit(0)
        # Repeat Student #
        elif 'R' in usrCmd:
            print( f"<<< REPEAT {self.stdNam} Evaluation! <<<" )
            rtnState['loop'] = "continue"
        # Back to Previous Student #
        elif 'P' in usrCmd:
            rtnState['iDelta'] = -1
            print( "^^^ PREVIOUS STUDENT ^^^" )
            rtnState['reverse'] = True
            rtnState['loop'   ] = "continue"
        # Next Student List File #
        elif 'E' in usrCmd:
            print( "!///! END LIST !///!" )
            rtnState['loop'] = "break"
        # Accept Previous Data #
        elif ('A' in usrCmd) or ('ACCEPT' in usrCmd):
            rtnState['flags'].append( 'acceptPrev' )
        return rtnState


    def run_grading_session( self ):
        """ Find it, Compile it, Run it, Look at it! """
        ii = 0
        N  = len( self.students )
        try:
            while ii < N:
                studentNam = self.students[ii]
                d, _       = self.get_student_dir( studentNam )
                if d is None:
                    print( f"NO directory for {studentNam}!" )
                    ii += 1
                    continue
                studentStr = str( d.split('/')[-1] )

                if studentStr[:2] == "__":
                    print( f"Admin Dir: {studentStr}" )
                    ii += 1
                    continue

                try:
                    _ = int( studentStr[:2] )
                    print( f"Admin Dir: {studentStr}" )
                    sleep( 0.25 )
                    ii += 1
                    continue
                except ValueError:
                    pass

                prevDeductions = None
                if studentStr in self.state["evals"]:
                    if not len( self.state["evals"][ studentStr ]["Feedback"]["RESUBMIT"] ):
                        print( f"{studentStr} was graded!, Skipping ..." )
                        ii += 1
                        continue
                    else:
                        print( f"\nGrade RESUBMIT for {self.stdNam}\n" )
                        if len( self.state["evals"][ studentStr ]["Feedback"]["DEDUCTIONS"] ):
                            prevNotes = list()
                            for deduct in self.state["evals"][ studentStr ]["Feedback"]["DEDUCTIONS"]:
                                parts = f"{deduct}".split(',')
                                nuStr = parts[0] + " (Prev. Submission, Cumulative), " + (",".join( parts[1:] ) if (len( parts ) > 1) else "")
                                prevNotes.append( nuStr )
                            prevDeductions = { "Feedback" : { "DEDUCTIONS" : prevNotes } }

                # Allow search/cancel/quit at the start of each list
                print( f"\nAbout to evaluate {studentNam} ... \n" )
                stateChange = self.run_menu()
                
                # Handle Student Search --> Index Jump #
                if stateChange['index'] >= 0:
                    ii = stateChange['index']
                    continue
                
                # Handle Missing Submission #
                if self.get_student_prefix( studentStr ) is None:
                    print( f"Student not found!: {self.get_student_prefix( studentStr )} from {studentStr}" )
                    ii += 1
                    continue
                # Else: Save Current State #
                else:
                    self.store_grading_state()

                if 'acceptPrev' in stateChange['flags']:
                    print( f"Accept current state for {self.stdNam}" )
                    ii += 1
                    continue

                self.run_student_report( studentStr, d, carryover = prevDeductions )
                self.state["lastStudent"] = studentNam
                ii += 1
            self.store_grading_state()
        except KeyboardInterrupt:
            self.shutdown()
    


########## MAIN ####################################################################################
if __name__ == "__main__":
    grin = GraphicsInspector( _CONFIG_PATH )
    grin.startup()
    grin.run_grading_session()
    sleep( 1.5 )
    grin.shutdown()

    

        

        

        
            
                

            
                
            

            

        
