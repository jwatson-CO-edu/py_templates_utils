import os, subprocess

from utils import out_line, env_get


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
