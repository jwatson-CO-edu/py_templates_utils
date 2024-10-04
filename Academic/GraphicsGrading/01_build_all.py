import os, subprocess, shutil, stat


def out_line( outFile, outStr ):
    """ Print and write the output with a newline """
    print( outStr )
    outStr += '\n'
    outFile.write( outStr )


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
    process = subprocess.Popen( f"grep -n \"{pattern}\" {hwDir}/*.c*", 
                                shell  = True,
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE )


    # wait for the process to terminate
    out, _ = process.communicate()
    return out.decode()



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


def get_ordered_students( listPath ):
    """ Prep student list for searching """
    students = list()
    with open( listPath, 'r' ) as f:
        lines = f.readlines()
        for line in lines:
            if len( line ) > 2:
                students.append( line.replace('-','').lower().split() )
    students.sort( key = lambda x: x[1] )
    return students


def get_student_prefix( stdntLst, query ):
    """ Get a prefix that orders the folders """
    for stdnt in stdntLst:
        if (stdnt[0] in query) and (stdnt[1] in query):
            return f"{stdnt[1]}_{stdnt[0]}_"
    return None


def get_student_name( stdntLst, query ):
    """ Get a prefix that orders the folders """
    for stdnt in stdntLst:
        if (stdnt[0] in query) and (stdnt[1] in query):
            first = f"{stdnt[0][0].upper()}{stdnt[0][1:]}"
            secnd = f"{stdnt[1][0].upper()}{stdnt[1][1:]}"
            return f"{first} {secnd}"
    return None


def p_executable( path ):
    """ Return True if the file can be run """
    # Author: ssam, https://ubuntuforums.org/showthread.php?t=1457094&s=d79fc51840d2783bb1461f9a049b7e03&p=9138623#post9138623
    return bool( os.access(path, os.X_OK) )


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
                    if (".c.o" not in elems[0]) and (".cpp.o" not in elems[0]) and ("all" not in elems[0]):
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


if __name__ == "__main__":

    _LIST_PATH  = "MyStudents.txt"
    _BAD_DIR    = '00_NOTIFY'
    _GOOD_DIR   = '01_OK'
    _ALWAYS_PIE = True 
    _TXT_READER = 'xed'
    _BAD_PATTRN = "Project("

    subdirs = [ f.path for f in os.scandir() if f.is_dir() ]
    subdirs.sort()
    reports = list()

    students  = get_ordered_students( _LIST_PATH )
    ruleNames = ['', 'hw4', 'hw04', 'Projection', 'projection',]
    N_stdnts  = len( students )

    os.makedirs( _BAD_DIR , exist_ok = True )
    os.makedirs( _GOOD_DIR, exist_ok = True )
    

    for i, d in enumerate( subdirs ):
        studentStr = str( d.split('/')[-1] )
        if get_student_prefix( students, studentStr ) is None:
            continue

        reportPath = studentStr + ".txt"
        runStudent = True
        with open( reportPath, 'w' ) as f:
            out_line( f, f"########## Student: {studentStr} ##########\n\n" )
            out_line( f, f"Hello {get_student_name( students, studentStr )}!\nTake note of the compilation errors shown below! (You can ignore make rules not in your Makefile.)\n\n" )
            
            hwDir = dig_for_Makefile( d )
            depth = str( hwDir ).count('/')

            if hwDir is not None:
                out_line( f, f"Makefile DEPTH: {depth}\n" )
                out_line( f, f"Makefile is here: {hwDir}\n" )
            else:
                out_line( f, f"FAILURE: NO MAKEFILE IN THIS SUBMISSION\n" )
                runStudent = False

            make_clean( hwDir )

            if runStudent:

                if _ALWAYS_PIE:
                    modify_makefile_to_disable_PIE( hwDir )

                for rule in ruleNames:
                    runStudent = make_in_dir_from_rule_with_output( hwDir, rule, f )
                    if runStudent:
                        break
                
            if runStudent:
                out_line( f, f"########## Compilation SUCCESS! ##########\n\n" )
                fExec      = find_executable( hwDir )
                runStudent = (fExec is not None) and os.path.isfile( fExec )

            if len( _BAD_PATTRN ):
                match = scrape_source( hwDir, _BAD_PATTRN )
                if len( match ):
                    out_line( f, f"PROHIBITED PATTERN FOUND:\n{match}\n" )
                else:
                    print( f"No prohibited text found!\n" )

            fRead = find_README( hwDir )
            if fRead is not None:
                os.system( f"{_TXT_READER} {fRead}" )
                print( f"Opened README at {fRead}" )
            else:
                out_line( f, f"BAD: >>NO<< README provided to the grader!" )

            if runStudent:
                print( f"Executable NAME: {str(fExec).split('/')[-1]}\n" )
                print( f"Running ./{fExec} ..." )
                os.system( f"./{fExec}" )
            else:
                out_line( f, f"ERROR: >>NO<< executable found at the expected location!" )
        
            if not runStudent:
                out_line( f, f"########## NOTIFY Student! ##########\n\n" )
            

        if runStudent:
            shutil.move( reportPath, os.path.join( _GOOD_DIR, reportPath ) )
        else:
            shutil.move( reportPath, os.path.join( _BAD_DIR , reportPath ) )

        if i < (N_stdnts-1):
            _ = input( "Press [Enter] to run the next report ..." )
