"""
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339
"""

import os, time

step = 0.25

def stopwatch():
    t     = 0
    timer = None
    bgn   = time.time()
    try:
        print( "< Stopwatch >" )
        while 1:
            mins, secs = divmod(t, 60)
            timer = '{:02d}m : {:.2f}s'.format(int(mins), secs)
            print( timer, end="\r" ) # https://stackoverflow.com/a/17391457
            time.sleep( step )
            t += step
    except KeyboardInterrupt:
        t = time.time() - bgn
        mins, secs = divmod(t, 60)
        timer = '{:02d}m : {:.2f}s'.format(int(mins), secs)
        print( "Timer ended at:", timer )
        duration =   0.5  # seconds
        freq     = 550 #440  # Hz
        os.system( 'play -nq -t alsa synth {} sine {}'.format(duration, freq) )

stopwatch()