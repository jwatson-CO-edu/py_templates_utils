"""
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339
"""

import os, time

# define the countdown func.
def countdown( t ):

    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print( timer, end="\r" ) # https://stackoverflow.com/a/17391457
        time.sleep(1)
        t -= 1

    print("Time's up!!")
    duration =   2  # seconds
    freq     = 550 #440  # Hz
    os.system( 'play -nq -t alsa synth {} sine {}'.format(duration, freq) )


# input time in seconds
t = input("Enter the time in seconds: ")

# function call
countdown(int(t))
