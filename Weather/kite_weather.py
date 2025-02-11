import os
from ast import literal_eval

import numpy as np

# temprKey = "Temperature"
# speedKey = "Wind Speed"
# drctnKey = "Wind Direction"

outPath = os.path.expanduser( "~/py_templates_utils/data/kiteWeather.txt" )


if __name__ == "__main__":
    with open( outPath, 'r' ) as f:
        
        lines = f.readlines()

        temp = literal_eval( lines[0] )
        wSpd = literal_eval( lines[1] )
        wDir = literal_eval( lines[2] )

        tmpMn = np.mean( temp )
        wSpMn = np.mean( wSpd )
        wDrMn = np.mean( wDir )
        wSpSt = np.std( wSpd )
        wDrSt = np.std( wDir )

        print( "Let's go fly a kite?" )

        print( f"Temperature: {tmpMn:.1f}F" )

        print( f"Wind Speed:  {wSpMn:.1f} ± {wSpSt:.1f}", end = ', ' )
        if wSpMn < 8.0:
            print( "Weak", end = ', ' )
        elif wSpMn < 10.0:
            print( "Marginal", end = ', ' )
        elif wSpMn < 17.0:
            print( "Good", end = ', ' )
        else:
            print( "Excessive", end = ', ' )
        if wSpMn >= 8.0:
            if wSpSt < 2.0:
                print( "Solid" )
            elif wSpSt < 4.0:
                print( "Variable" )
            else:
                print( "Unstable" )
        else:
            print( "☹" )

        print( f"Direction:   {wDrMn:.1f} ± {wDrSt:.1f}", end = ', ' )
        if wDrSt < 15.0:
            print( "Steady" )
        elif wDrSt < 30.0:
            print( "Wandering" )
        else:
            print( "Chaotic" )