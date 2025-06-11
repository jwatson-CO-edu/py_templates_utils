########## INIT ####################################################################################

##### Imports #####
### Standard ###
import os, subprocess, shutil, json
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


def attempt_normal_scan( fPath, fOut ):
    """ Attempt to determine if normals are correctly formed """
    f_NormRd = False
    f_3vrtcs = False
    nrm_i    = None
    pts_i    = [None,None,None,]
    ptDex    = 0
    accept   = np.radians( 10.0 )
    nFound   = False
    glNorm   = False
    nonUnt   = False

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
                if ("glNormal3d" in lnTkns) or ("glNormal3f" in lnTkns):
                    nFound = True
                    if f_NormRd and (not f_3vrtcs):
                        print( f"\tUNFINISHED triangle near line {j+1}" )
                    elif f_NormRd and (ptDex > 3):
                        print( f"\tSURPLUS points near line {j+1}" )
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
                    nrm_c    = vec_unit( np.cross( s0, s1 ) )
                    err_i    = angle_between( nrm_i, nrm_c )
                    if err_i > accept:
                        out_line( fOut, f"\n\tBAD NORMAL before line {j+1}, Err = {err_i:.3f} rad, {nrm_i} -vs- {nrm_c}" )
                    else:
                        print( '.', end='', flush=True )
            except Exception as e:
                print( f"~Line {j+1}: Norm Parser Fault, {e}" )
    if nonUnt and (not glNorm):
        out_line( fOut, f"\n\tNon-unit normals *without* GL_NORMALIZE enabled!" )
    print()
    return nFound





########## GRADER CLASS TO GRADE THE CLASS #########################################################

class GraphicsInspector:
    """ GRIN: CSCI 4/5229 Grading Utility """

    ##### Init ############################################################

    def get_stored_grading_state( self, fPath ):
        """ Get the local stored state """
        self.state = None
        if os.path.isfile( fPath ):
            with open( fPath, 'r' ) as f:
                self.state = json.load( f )
        else:
            self.state = {"lastStudent": env_get("_STATE_INT") }
        return self.state


    def store_grading_state( self, fPath ):
        """ Set the local stored state """
        with open( fPath, 'w' ) as f:
            json.dump( self.state, f )


    def get_ordered_students( self, listPath ):
        """ Prep student list for searching """
        self.students = list()
        with open( listPath, 'r' ) as f:
            lines = f.readlines()
            for line in lines:
                if len( line ) > 2:
                    self.students.append( line.replace('-','').lower().split() )
        self.students.sort( key = lambda x: x[1] )
        return self.students


    def __init__( self, configPath ):
        """ Set up the inspector for a grading session """
        read_config_into_env( configPath )
        try:
            self.get_stored_grading_state( env_get("_STATE_PTH") )
        except Exception as e:
            self.state = dict()
        self.subdirs = [ f.path for f in os.scandir() if f.is_dir() ]
        self.subdirs.sort()
        self.reports = list()
        self.get_ordered_students( env_get("_LIST_PATH") )
        self.N_stdnts = len( self.students )
        os.makedirs( env_get("_BAD_DIR" ), exist_ok = True )
        os.makedirs( env_get("_GOOD_DIR"), exist_ok = True )


    ##### File Operations #################################################
    
    def unzip_all( self ):
        """ Unzip all student submissions """
        count    = 0
        zpPaths  = [path for path in os.listdir() if ".zip" in path]        
        zpPaths.sort()

        for zp_i in zpPaths:
            folder = zp_i.split( '.' )[0]
            prefix = self.get_student_prefix( folder )
            
            if prefix is not None:
                folder = f"{prefix}{folder}"
                count += 1
                print( f"About to unpack {zp_i}\n\tto {folder}...", end='' )

                try:
                    shutil.unpack_archive( zp_i, folder )
                    print( "SUCCESS" )
                except Exception as e:
                    print( f"FAILURE: {e}" )

        print( f"Expanded {count} student submissions!" )


    ##### Grading #########################################################

    def get_student_prefix( self, query ):
        """ Get a prefix that orders the folders """
        for stdnt in self.students:
            if (stdnt[0] in query) and (stdnt[1] in query):
                return f"{stdnt[1]}_{stdnt[0]}_"
        return None


    def get_student_name( self, query ):
        """ Get a prefix that orders the folders """
        for stdnt in self.students:
            if (stdnt[0] in query) and (stdnt[1] in query):
                first = f"{stdnt[0][0].upper()}{stdnt[0][1:]}"
                secnd = f"{stdnt[1][0].upper()}{stdnt[1][1:]}"
                return f"{first} {secnd}"
        return None


    def run_student_report( self, studentStr, studentDir ):
        """ Get info on student submission and generate a report about it """
        reportPath = studentStr + ".txt"
        runStudent = True
        with open( reportPath, 'w' ) as f:
            out_line( f, f"########## Student: {studentStr} ##########\n\n" )
            out_line( f, f"Hello {self.get_student_name( studentStr )}!\nTake note of the compilation errors shown below! (You can ignore make rules not in your Makefile.)\n\n" )
            
            hwDir = dig_for_Makefile( studentDir )
            depth = str( hwDir ).count('/')

            if hwDir is not None:
                out_line( f, f"Makefile DEPTH: {depth}\n" )
                out_line( f, f"Makefile is here: {hwDir}\n" )
            else:
                out_line( f, f"FAILURE: NO MAKEFILE IN THIS SUBMISSION\n" )
                runStudent = False

            make_clean( hwDir )

            out_line( f, f"##### Normal Scan for: {studentStr} #####\n" )
            srcPaths = source_and_header_full_paths( hwDir )
            for sPath in srcPaths:
                out_line( f, f"\n### Normal Scan for: {str(sPath).split('/')[-1]} ###\n" )
                attempt_normal_scan( sPath, f )

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

            if len( env_get("_BAD_PATTRN") ):
                match = scrape_source( hwDir, env_get("_BAD_PATTRN") )
                if len( match ):
                    out_line( f, f"EXAMINE THIS LIST MATCHING \"{env_get('_BAD_PATTRN')}\":\n{match}\n" )
                else:
                    print( f"No prohibited text found!\n" )

            fRead = find_README( hwDir )
            if fRead is not None:
                os.system( f"{env_get('_TXT_READER')} {fRead}" )
                print( f"Opened README at {fRead}" )
            else:
                out_line( f, f"BAD: >>NO<< README provided to the grader!" )

            runStudent = (fExec is not None) and os.path.isfile( fExec )
            if runStudent:
                print( f"Executable NAME: {str(fExec).split('/')[-1]}\n" )
                print( f"Running ./{fExec} ..." )
                os.system( f"./{fExec}" )
            else:
                os.system( f"./{hwDir}/{env_get('_GOOD_NAME')}" )
                out_line( f, f"ERROR: >>NO<< executable found at the expected location!" )
        
            if not runStudent:
                out_line( f, f"########## NOTIFY Student! ##########\n\n" )
            

        if runStudent:
            shutil.move( reportPath, os.path.join( env_get("_GOOD_DIR"), reportPath ) )
        else:
            shutil.move( reportPath, os.path.join( env_get("_BAD_DIR") , reportPath ) )


    def run_grading_session( self ):
        """ Find it, Compile it, Run it, Look at it! """
        for i, d in enumerate( self.subdirs ):
            studentStr = str( d.split('/')[-1] )
            if self.state["lastStudent"] != env_get("_STATE_INT"):
                if self.state["lastStudent"] != studentStr:
                    continue
                else:
                    self.state["lastStudent"] = env_get("_STATE_INT")

            if self.get_student_prefix( studentStr ) is None:
                continue
            else:
                self.store_grading_state( env_get("_STATE_PTH") )

            self.run_student_report( studentStr, d )

            if i < (self.N_stdnts-1):
                _ = input( "Press [Enter] to run the next report ..." )
    


########## MAIN ####################################################################################
if __name__ == "__main__":
    grin = GraphicsInspector( _CONFIG_PATH )
    grin.unzip_all()
    grin.run_grading_session()

    

        

        

        
            
                

            
                
            

            

        
