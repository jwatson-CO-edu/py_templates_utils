# https://docs.python.org/3/howto/urllib2.html

########## INIT ####################################################################################

import urllib.request, os
from math import ceil
from collections import deque
from time import sleep



_TRGT_URL = "https://sundowner.colorado.edu/weather/atoc1/"
_PERIOD_M = 15
_SURVEY_M = 60 * 2
_MAX_LEN  = int( ceil( _SURVEY_M / _PERIOD_M ) )
temprKey  = "Temperature"
speedKey  = "Wind Speed"
drctnKey  = "Wind Direction"
outPath   = os.path.expanduser( "~/py_templates_utils/data/kiteWeather.txt" )

temp = deque( maxlen = _MAX_LEN )
wSpd = deque( maxlen = _MAX_LEN )
wDir = deque( maxlen = _MAX_LEN )


def val_from_line( line ):
    """ Get the current value from the ATOC table """
    data = line.split( "<td align=center>" )
    return float( data[1].split( "</td>" )[0] )


def fetch_ATOC_datapoint():
    """ Get relevant data from ATOC """
    global temp, wSpd, wDir
    with urllib.request.urlopen( _TRGT_URL ) as response:
        trgtHTML = response.readlines()
        trgtHTML = [item.decode().replace('\n','') for item in trgtHTML]
        for line in trgtHTML:
            # print( line )
            if temprKey in line:
                datum = val_from_line( line )
                temp.append( datum )
                print( datum )
            elif speedKey in line:
                datum = val_from_line( line )
                wSpd.append( datum )
                print( datum )
            elif drctnKey in line:
                datum = val_from_line( line )
                wDir.append( datum )
                print( datum )



########## MAIN ####################################################################################
if __name__ == "__main__":
    while 1:
        fetch_ATOC_datapoint()
        with open( outPath, 'w' ) as f:
            f.write( f"{list( temp )}\n" )
            f.write( f"{list( wSpd )}\n" )
            f.write( f"{list( wDir )}\n" )
        sleep( _PERIOD_M * 60.0 )