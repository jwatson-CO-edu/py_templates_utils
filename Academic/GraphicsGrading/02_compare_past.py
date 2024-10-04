########## INIT ####################################################################################

import shutil, os, subprocess



########## REPORTING FUNCTIONS #####################################################################

def copy_past_submissions( pastDir, pastPre ):
    """ Move past submissions into the root folder and tag """
    subdirs = [ f.path for f in os.scandir( pastDir ) if f.is_dir() ]
    for sDir in subdirs:
        # print( sDir )
        mDir = f"{pastPre}{str( sDir ).split('/')[-1]}" 
        shutil.move( sDir, mDir )
        print( f"Move {sDir} --to-> {mDir}" )


def generate_MOSS_report():
    process = subprocess.Popen( f"./moss -l c -d ./*/*.h ./*/*.c ./*/*.hpp ./*/*.cpp ./*/*/*.h ./*/*/*.c ./*/*.hpp ./*/*/*.cpp", 
                                shell  = True,
                                stdout = subprocess.PIPE, 
                                stderr = subprocess.PIPE )
    out, err = process.communicate()
    out = out.decode()
    err = err.decode()
    errcode = process.returncode

    print( f"MOSS terminated with code: {errcode}" )
    print( out )

    return out



########## MAIN ####################################################################################

if __name__ == "__main__":

    _REPORT_PATH = "AAAA_MOSS_Report.txt"
    _PAST_ROOT   = "F23"
    _PAST_PATH   = f"{_PAST_ROOT}/hw3/"
    _PAST_PREFIX = "ZZZZ_"

    copy_past_submissions( _PAST_PATH, _PAST_PREFIX )
    if not os.path.isfile( _REPORT_PATH ):
        with open( _REPORT_PATH, 'w' ) as f:
            f.write( generate_MOSS_report() )
