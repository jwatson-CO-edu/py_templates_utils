import shutil, os



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



if __name__ == "__main__":

    _LIST_PATH = "MyStudents.txt"

    students = get_ordered_students( _LIST_PATH )
    count    = 0
    zpPaths  = [path for path in os.listdir() if ".zip" in path]
    
    zpPaths.sort()

    for zp_i in zpPaths:
        folder = zp_i.split( '.' )[0]
        prefix = get_student_prefix( students, folder )
        
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
    