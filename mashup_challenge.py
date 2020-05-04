from libs.Parsing import parse_lines
from random import randrange

# === Emitters ===

class Repeater:
    """ Select lines from a file """
    
    def __init__( self , inputFileName ):
        """ Read lines from a file, while ignoring comments """
        self.fPath = inputFileName
        self.lines = parse_lines( self.fPath , str )
        self.mode  = "default"
        self.index = 0
        
    def get_elem( self , bigDex ):
        """ Return a corrected index with wrapping """
        return self.lines[ bigDex % len( self.lines ) ]
        
    def get_next( self ):
        """ Get the next line in sequence """
        rtnStr = self.get_elem( self.index )
        self.index += 1
        return rtnStr
    
class Randomizer( Repeater ):
    """ Choose elements without replacement, reset when exhausted """
    
    def reset( self ):
        """ Set the line pool to a copy of the file's contents """
        self.pool = self.lines[:]
    
    def __init__( self , inputFileName ):
        """ Read lines from a file, while ignoring comments """
        super().__init__( inputFileName )
        self.reset()
        
    def get_next( self ):
        """ Draw the next sample, without replacement, Reset when exhausted """
        if len( self.pool ) == 0:
            self.reset()
        rtnDex = randrange( len( self.pool ) )
        return self.pool.pop( rtnDex )
        
# ___ End Emit ___

class Composer:
    """ A composition of Emitters """
    
    def __init__( self ):
        """ Set up a list of emitters """
        self.emitters = []
        
    def add_emitter( self , obj ):
        """ Append emitter to the list """
        self.emitters.append( obj )
        
    def get_next( self , sep = "" ):
        """ Compose a string that contains the output of all emitters, in order """
        totStr = ""
        for eDex , emt in enumerate( self.emitters ):
            totStr += str( emt.get_next() ) + ( sep if ( sep and eDex < ( len( self.emitters ) - 1 ) ) else " " )
        return totStr
    
    def print_next( self ):
        """ Print the next string in the sequence """
        print( self.get_next() )
        
    def gets_to_file( self , N , outPath , showSeq = 1 ):
        """ Write `N` calls to `get_next` to a file """
        import os
        outFile = open( outPath , 'w' )
        for i in range( N ):
            outFile.write( ( (str(i+1).rjust( len(str(N)) , ' ') + ". ") if showSeq else "" ) + self.get_next() + os.linesep )
        outFile.close()
        
if __name__ == '__main__':
    comp = Composer()
    comp.add_emitter( Repeater( "input/MayDwellers2020.txt" ) )
    comp.add_emitter( Randomizer( "input/types.txt" ) )
    comp.add_emitter( Randomizer( "input/roles.txt" ) )
    comp.gets_to_file( 31 , "output/MayDwellersMashup2020.txt" )
    