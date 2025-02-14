import shutil , os , sys

_TEMPNAME = "temp.txt"
_TABWIDTH = 4

if __name__ == "__main__":
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    # 1. Copy the file.
    shutil.copy2( termArgs[0] , _TEMPNAME )
    
    # 2. Delete the original
    os.remove( termArgs[0] )    
    
    # 3. Open a file with the same name as the original
    with open( termArgs[0] , 'w' ) as fWr:
        with open( _TEMPNAME , 'r' ) as fRd:
            while 1:  
                # read by character 
                char = fRd.read( 1 )           
                if not char:  
                    break  
                elif char == '\t':
                    fWr.write( ' ' * _TABWIDTH )
                else:
                    fWr.write( char )
                    
    # 4. Delete the temp file
    os.remove( _TEMPNAME ) 