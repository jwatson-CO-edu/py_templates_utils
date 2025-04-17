"""
NOTE: `sudo apt install sox`
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339
"""

import os, time

# define the countdown func.
def countdown( t ):

    while t >= 0:
        try:
            mins, secs = divmod(t, 60)
            if mins > 59:
                hour, mins = divmod(mins, 60)
                timer = '{:02d}:{:02d}:{:02d}'.format(hour, mins, secs)
            else:
                timer = '   {:02d}:{:02d}'.format(mins, secs)
            print( timer, end="\r" ) # https://stackoverflow.com/a/17391457
            time.sleep(1)
            t -= 1
        except KeyboardInterrupt:
            print( f"User ended countdown with {t} seconds remaining!\n" )
            exit()

    print("Time's up!!")
    duration =  10  # seconds
    freq     = 550 #440  # Hz
    os.system( 'play -nq -t alsa synth {} sine {}'.format(duration, freq) )


def get_sec( timeStr ):
    """Get seconds from string with format "HH:MM:SS" """
    # Adapted from work by Taskinoor Hasan, https://stackoverflow.com/a/6402859
    parts = timeStr.split(':')
    parts.reverse()
    rtnSec = 0
    for i, prt in enumerate( parts ):
        rtnSec += int( prt ) * 60**i    
    return rtnSec
  
  
def parse_expr_to_seconds( secExp ):
    """ Parse either "HH:MM:SS" or a math expression as a number of seconds """
    if ':' in secExp: # A. If colon(s) present, then Assume HH:MM:SS
        return get_sec( secExp )
    return int( eval( secExp ) ) # Else assume math expression


# input time in seconds
tExpr = input("Enter the time in seconds (HH:MM:SS or math allowed): ")

# Compute seconds and begin countdown
countdown( parse_expr_to_seconds( tExpr ) )
