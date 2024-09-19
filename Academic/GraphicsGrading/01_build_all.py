import os, subprocess, shutil

subdirs = [ f.path for f in os.scandir() if f.is_dir() ]
subdirs.sort()
reports = list()


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


def make_in_dir_from_rule_with_output( hwDir, rule, f ):
    """ Make the rule in the child directory and report results """
    runStudent = True
    try:
        process = subprocess.Popen( f"make {rule} -C '{hwDir}'", 
                                    shell  = True,
                                    stdout = subprocess.PIPE, 
                                    stderr = subprocess.PIPE )

        # wait for the process to terminate
        out, err = process.communicate()
        out = out.decode()
        err = err.decode()
        errcode = process.returncode

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
                students.append( line.lower().split() )
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


if __name__ == "__main__":

    _LIST_PATH = "MyStudents.txt"
    _BAD_DIR   = '00_NOTIFY'
    _GOOD_DIR  = '01_OK'

    students  = get_ordered_students( _LIST_PATH )
    ruleNames = ['', 'lorenz', 'hw2', 'hw02',]

    os.makedirs( _BAD_DIR , exist_ok = True )
    os.makedirs( _GOOD_DIR, exist_ok = True )
    
    for d in subdirs:
        studentStr = str( d.split('/')[-1] )
        if get_student_prefix( students, studentStr ) is None:
            continue

        reportPath = studentStr + ".txt"
        runStudent = True
        with open( reportPath, 'w' ) as f:
            out_line( f, f"########## Student: {studentStr} ##########\n\n" )
            out_line( f, f"Hello {get_student_name( students, studentStr )}!\nTake note of the compilation errors shown below! (You can ignore make rules not in your Makefile.)\n\n" )
            
            hwDir = dig_for_Makefile( d )

            if hwDir is not None:
                out_line( f, f"Makefile is here: {hwDir}\n" )
            else:
                out_line( f, f"FAILURE: NO MAKEFILE IN THIS SUBMISSION\n" )
                runStudent = False

            if runStudent:
                for rule in ruleNames:
                    runStudent = make_in_dir_from_rule_with_output( hwDir, rule, f )
                    if runStudent:
                        break
                
            if runStudent:
                out_line( f, f"########## Compilation SUCCESS! ##########\n\n" )
            else:
                out_line( f, f"########## NOTIFY Student! ##########\n\n" )

        if runStudent:
            shutil.move( reportPath, os.path.join( _GOOD_DIR, reportPath ) )
        else:
            shutil.move( reportPath, os.path.join( _BAD_DIR , reportPath ) )
