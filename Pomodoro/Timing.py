from time import time
from math import floor
from dicttoxml import dicttoxml # https://www.tutorialspoint.com/How-to-serialize-Python-dictionary-to-XML

# === Timing / Benchmarking ============================================================================================

class HeartRate: # NOTE: This fulfills a purpose similar to the rospy rate
    """ Sleeps for a time such that the period between calls to sleep results in a frequency not greater than the specified 'Hz' """
    
    def __init__( self , Hz ):
        """ Create a rate object with a Do-Not-Exceed frequency in 'Hz' """
        self.period = 1.0 / Hz; # Set the period as the inverse of the frequency , hearbeat will not exceed 'Hz' , but can be lower
        self.last = time()
        
    # NOTE: `get_remainder` and `mark_time` drive internal and external timekeeping

    def get_remainder( self ):
        """ Return the remainder of seconds in this period """
        return max( self.period - ( time() - self.last ) , 0.0 )
    
    def mark_time( self ):
        """ Log the end of a cycle """
        self.last = time()
    
    def sleep( self ):
        """ Sleep for a time so that the frequency is not exceeded """
        time.sleep( self.get_remainder() ) # 1. Sleep for remaining time
        self.mark_time() # ----------------- 2. Log the last time object waited

class Stopwatch( object ):
    """ Timer for benchmarking """

    def __init__( self ):
        """ Init with watch started """
        self.strtTime = time()
        self.stopTime = infty

    def start( self ):
        self.strtTime = time()

    def stop( self ):
        self.stopTime = time()

    def duration( self ):
        return self.stopTime - self.strtTime

    def elapsed( self ):
        return time() - self.strtTime
   
# == Time Accounting ==   
   
class Duration:
    """ Model a duration of up to a week """
    
    div = { 'w' : 60 * 60 * 24 * 7,
            'd' : 60 * 60 * 24,
            'h' : 60 * 60,
            'm' : 60 ,
            's' : 1  }
    seq = [ 'w' , 'd' , 'h' , 'm' , 's' ]
    rpl = { 'w':2 , 'd':2 , 'h':2 , 'm':2 , 's':5 }
    
    def __init__( self , US = None , w = 0 , d = 0 , h = 0 , m = 0 , s = 0 ):
        """ Init denominations """
        # Time Math
        # self.divSeq = [ 'w' , 's' , 'm' , 'h' , 'd' ] # Sequence of divisiors
        if US == None:
            self.w  = w # Weeks
            self.d  = d # Days
            self.h  = h # Hours
            self.m  = m # Minutes
            self.s  = s # Seconds (Can be fractional)
            self.US = 0.0 # Underlying Seconds
            self.accumulate_US()
            self.normalize_US()
        else:
            self.w  = 0.0 # Weeks
            self.d  = 0.0 # Days
            self.h  = 0.0 # Hours
            self.m  = 0.0 # Minutes
            self.s  = 0.0 # Seconds (Can be fractional)
            self.US = US
            self.normalize_US()
    
    def normalize_US( self ):
        """ Set the denominations from the Underlying Seconds """
        totS = self.US
        for tDiv in Duration.seq:
            sDiv = Duration.div[ tDiv ]
            if tDiv != 's':
                setattr( self , tDiv ,  int( floor( totS / sDiv ) )  )
                totS = totS % sDiv
            else:
                setattr( self , tDiv ,  totS  )
                
    def accumulate_US( self ):
        """ Set the Underlying Seconds from the Denominations """
        self.US = 0.0
        for tDiv in Duration.seq:
            sDiv = Duration.div[ tDiv ]
            self.US += getattr( self , tDiv ) * Duration.div[ tDiv ]
    
    def from_list( self , timeList ):
        """ Parse a list as a duration """
        tLen = len( timeList )
        if tLen > 5:
            raise ValueError( "Input format is list " + str( Duration.seq ) +
                              " from most significant to seconds!" )
        seqSlice = Duration.seq[ -tLen : ]
        
        self.US = 0
        for tDex , tDiv in enumerate( seqSlice ):
            self.US += Duration.div[ tDiv ] * timeList[ tDex ]
        self.normalize_US()
            
    def to_list( self ):
        """ Convert to a list """
        bgnDex = 0
        for bDex , tDiv in enumerate( Duration.seq ):
            bgnDex = bDex
            if getattr( self , tDiv ) != 0:
                break
        seqSlice = Duration.seq[ bgnDex : ]
        rtnList  = []
        for tDiv in seqSlice:
            rtnList.append( getattr( self , tDiv ) )
        return rtnList
            
    def __sub__( self , other ):
        """ Subtract another `Duration` from this one """
        return Duration( US = self.US - other.US )
    
    def __str__( self ):
        """ Return a string representation of the `Duration` """
        bgnDex = 0
        for bDex , tDiv in enumerate( Duration.seq ):
            bgnDex = bDex
            if getattr( self , tDiv ) != 0:
                break
        seqSlice = Duration.seq[ bgnDex : ]
        rtnStr   = ""
        for tDex , tDiv in enumerate( seqSlice ):
            tNum = getattr( self , tDiv )
            if tDiv == 's':
                segment = "{:.3f}".format( tNum )
            else:
                segment = str( tNum )
            # print( "This segment should have length" , Duration.rpl[ tDiv ] )
            rtnStr += segment.rjust( Duration.rpl[ tDiv ] , '0' ) + \
                      ' ' + tDiv + " : "
        rtnStr = rtnStr[:-3]
        return rtnStr
            
    def to_dict( self ):
        """ Return a dictionary serialization representing this Duration """
        self.normalize_US()
        return {
            'w'  : self.w  , # Weeks
            'd'  : self.d  , # Days
            'h'  : self.h  , # Hours
            'm'  : self.m  , # Minutes
            's'  : self.s  , # Seconds 
            'US' : self.US , # Underlying seconds
        }

class Interval:
    """ Keep track of an interval of real time """
    
    def __init__( self , US = None , w = 0 , d = 0 , h = 0 , m = 0 , s = 0 , name = "" ):
        """ Set interval bookkeeping vars """
        self.bgn    = None 
        self.end    = None
        self.dur    = Duration( US = US , w = w , d = d , h = h , m = m , s = s )
        self.active = False
        self.paused = False
        self.remSec = self.dur.US
        self.name   = name
        
    def set_duration( self , w = 0 , d = 0 , h = 0 , m = 0 , s = 0 ):
        """ Create an underlying `Duration` object """
        self.dur = Duration( w = w , d = d , h = h , m = m , s = s )
        
    def get_remaining( self ):
        """ Update and Return the remaining time, Will be <0 if the duration has been exceeded """
        if self.active:
            self.remSec = self.end - time()
            return self.remSec
        else:
            return -1.0
    
    def start( self ):
        """ Set the beginning and end times if not paused, Otherwise update the end time and set status """
        self.active = True
        self.paused = False
        if not self.paused:
            self.bgn = time()
            self.end = self.bgn + self.dur.US
        else:
            self.end = self.bgn + self.remSec
        
    def pause( self ):
        """ Log the time remaining and set status to paused """
        self.get_remaining()
        self.paused = True
        
    def stop( self ):
        """ Make this interval inactive, Reset the remaining time to full """
        self.bgn    = None
        self.end    = None
        self.active = False
        self.paused = False
        self.remSec = self.dur.US
        
    def check_running( self ):
        """ Check if we are in the middle of this interval, Stop if we have surpassed """
        if not self.paused:
            self.get_remaining()
            if self.remSec <= 0:
                self.stop()
            return self.active
        else:
            return True
        
    def __str__( self ):
        """ Return a string representation of the time remaining """
        return str( Duration( US = self.remSec ) )
    
    def to_dict( self ):
        """ Serialize this object to hash """
        return {
            'duration'    : self.dur.to_dict() , 
            'paused'      : self.paused        ,
            's_remaining' : self.remSec        ,
            'name'        : self.name          ,
        }
        
    def to_xml( self , pathName = "pomoSettings.xml" ):
        """ Serialize this object to XML """
        # https://www.tutorialspoint.com/How-to-serialize-Python-dictionary-to-XML
        xml     = dicttoxml( self.to_dict() ) # Serialize
        xmlfile = open( pathName , 'w' )
        xmlfile.write( xml.decode() )
        xmlfile.close()
        
    
# __ End Accounting __

# ___ End Timing ___________________________________________________________________________________________________________________________