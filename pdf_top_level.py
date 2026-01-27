import os, shutil
from collections import deque

def get_PDF_files( searchDir = None, rtnLs = None ):
    """ Get all the filenames under `searchDir` that are suitable for per-month filing """
    if rtnLs is None:
        rtnLs = deque()
    files = None
    fldrs = None
    if searchDir is not None:
        # print( os.listdir( searchDir ) )
        files = [ item for item in os.listdir( searchDir ) if (os.path.isfile( os.path.join( searchDir, item ) ) and ("pdf" in f"{item}".lower())) ]
        fldrs = [ item for item in os.listdir( searchDir ) if os.path.isdir( os.path.join( searchDir, item ) )  ]
    else:
        # print( os.listdir() )
        files = [ item for item in os.listdir() if (os.path.isfile( item ) and ("pdf" in f"{item}".lower())) ]
        fldrs = [ item for item in os.listdir() if os.path.isdir( item )  ]
    if len( fldrs ):
        print( fldrs )
    for file in files:
        totPath = os.path.join( searchDir, file ) if (searchDir is not None) else file
        newPath = f"{totPath}".split('/')[-1]
        print( totPath, newPath )
        rtnLs.append( totPath )
        shutil.move( totPath, newPath )
    for fldr in fldrs:
        if searchDir is None:
            get_PDF_files( fldr, rtnLs )
        else:
            get_PDF_files( os.path.join( searchDir, fldr ), rtnLs )
    return rtnLs

if __name__ == "__main__":
    get_PDF_files()