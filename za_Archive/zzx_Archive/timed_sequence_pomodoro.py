"""
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339
"""
########## INIT & SETTINGS #############################################################################################


##### Imports #####
import os, time, signal, wrapper, curses
from pynput.keyboard import Key, Listener


##### Schedule #####
tProgram = [
    ( 2, "Work" ),
    ( 2, "Break" ),
]

##### Settings #####
duration =   1 # ----- Duration of tone [s]
freq     = 475 # ----- Tone sine frequency [Hz]
pauseKy  = Key.space # Pause key


##### Globals #####
running = True



########## POMODORO ####################################################################################################


def toggle_running( key ):
    """ When the pause key is pressed, toggle the running state """
    global running
    running = not running


def pomodoro( program ):
    """ A simple pomodoro timer """
    
    # A. Load first interval
    i = 0
    N = len( program )
    t = program[i][0]
    s = program[i][1]
    
    # B. Run program
    while 1:
        
        try:
        
            # 1. If the period has ended, then play tone and advance program
            if t <= 0:
                os.system( 'play -nq -t alsa synth {} sine {}'.format(duration, freq) )
                i = (i+1) % N
                t = program[i][0]
                s = program[i][1]
            
            # 2. Compute readable time denominations and fetch period title
            mins, secs = divmod( t, 60 )
            timer = f"{s}:".ljust(10) 
        
            # 3. If the timer is running, display time remaining and decrement it
            if running:
                timer += f"{mins:02}:{secs:02}"
                t -= 1
            # 4. Else timer is paused, display remaining but do not decrement it
            else:
                timer += f"PAUSED AT {mins:02}:{secs:02}"
                
            # 5. Print
            print( timer, end="\r" ) # https://stackoverflow.com/a/17391457
            time.sleep(1)

        except KeyboardInterrupt:
            print( f"\nUser ended countdown with {t} seconds remaining!\n" )
            exit()

    print("\nPROGRAM COMPLETE\n")
    
    

########## MAIN ########################################################################################################

if __name__ == '__main__':
    signal.signal( signal.SIGTSTP, toggle_running )
    pomodoro( tProgram )
    
