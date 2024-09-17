"""
## Resources ##
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339

## ~/.bashrc Command Alias ##
alias pomo='python $HOME/py_templates_utils/pomodoro.py'
"""
########## INIT & SETTINGS #############################################################################################


##### Imports #####
import os, time, curses


##### Schedules #####
tFocus = [
    ( 90 * 60, "Work"  ),
    ( 10 * 60, "Break" ),
]

tRealBreak = [
    ( 90 * 60, "Work"  ),
    ( 15 * 60, "Break" ),
]

tLongHaul = [
    ( 120 * 60, "Work"  ),
    (  10 * 60, "Break" ),
]

tWorkHardWalkHard = [
    ( 120 * 60, "Work"  ),
    (  20 * 60, "Break" ),
]

tEasy = [
    ( 60 * 60, "Work"  ),
    ( 10 * 60, "Break" ),
    ( 60 * 60, "Work"  ),
    ( 10 * 60, "Break" ),
    ( 60 * 60, "Work"  ),
    ( 10 * 60, "Break" ),
    ( 40 * 60, "Work"  ),
    ( 20 * 60, "Long Break" ),
]

tHustle = [
    ( 55 * 60, "Work"  ),
    (  5 * 60, "Break" ),
    ( 55 * 60, "Work"  ),
    (  5 * 60, "Break" ),
    ( 55 * 60, "Work"  ),
    (  5 * 60, "Break" ),
    ( 55 * 60, "Work"  ),
    ( 15 * 60, "Long Break" ),
]

tBeast = [
    ( 60 * 60, "Work"  ),
    (  5 * 60, "Break" ),
]

##### Settings #####
duration =   3 # ----- Duration of tone [s]
freq     = 475 # ----- Tone sine frequency [Hz]



########## POMODORO ####################################################################################################
    

def pomodoro( program ):
    """ A simple pomodoro timer """
    
    # Init Window #
    running = True
    titlePd = max( [len( item[1] ) for item in program] ) + 2
    stdscr  = curses.initscr() # initialize curses screen
    stdscr.nodelay(1) # ------- `getch()` and `getkey()` for the window become non-blocking
    curses.noecho() # --------- turn off auto echoing of keypress on to screen
    curses.cbreak() # --------- react to keys instantly, without requiring the Enter key to be pressed
    tIncr = 10*60 # ----------- Increment of time to add/subtract with p/m
    
    def clean():
        """ Return terminal to normal """
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
    
    # Draw Static Portion #
    stdscr.border(0)
    stdscr.addstr(5, 5, 'Pomodoro Timer', curses.A_BOLD)
    stdscr.addstr(6, 5, '[Space]: Pause, [n]: Next Interval, [r]: Restart Interval, [q]: Quit, [p]: Plus time, [m] Minus time', curses.A_NORMAL)
    
    # Load first interval #
    i = 0
    N = len( program )
    t = program[i][0]
    s = program[i][1]
    
    def advance_interval( restart = 0 ):
        """ Move to the next interval in the program """
        nonlocal i, t, s
        if not restart:
            i = (i+1) % N
        t = program[i][0]
        s = program[i][1]
    
    # Run Program #
    while 1:
        
        try:
        
            # 1. If the period has ended, then play tone and advance program
            if t <= 0:
                os.system( 'play -nq -t alsa synth {} sine {}'.format(duration, freq) )
                advance_interval()
                
            
            # 2. Compute readable time denominations and fetch period title
            mins, secs = divmod( t, 60 )
            timer = f"{s}:".ljust( titlePd ) 
        
            # 3. If the timer is running, display time remaining and decrement it
            if running:
                timer += f"{mins: 3}:{secs:02}"
                t -= 1
            # 4. Else timer is paused, display remaining but do not decrement it
            else:
                timer += f"PAUSED AT {mins: 3}:{secs:02}"
                
            # 5. Print
            stdscr.addstr( 8, 5, timer, curses.A_NORMAL )
            stdscr.refresh()
            
            # 5. Wait
            stdscr.timeout( 1000 )
            
            # 6. Fetch user command
            key = stdscr.getch()
            if key == ord( 'q' ): # Quit
                break
            elif key == ord( 'n' ): # Next Interval
                advance_interval()
            elif key == ord( 'r' ): # Restart Interval
                advance_interval( restart = 1 )
            elif key == ord(' '): # Pause
                stdscr.addstr( 8, 5, ' '*30, curses.A_NORMAL ) # Blank out the last time print b/c pause has a longer message
                running = not running
            elif key == ord('p'):  # Plus duration
                t += tIncr
            elif key == ord('m'):  # Plus duration
                t -= tIncr
                
        # Handle Ctrl-C #
        except KeyboardInterrupt:
            clean()
            print( f"\nUser ended countdown with {t} seconds of {s} remaining!\n" )
            exit()

    # Return terminal to normal #
    clean()
    print("\nPROGRAM COMPLETE\n")
    
    

########## MAIN ########################################################################################################

if __name__ == '__main__':
    # pomodoro( tEasy ) # 60/10 + Long Break 20
    # pomodoro( tBeast ) # 60/5 repeating
    # pomodoro( tFocus ) # 90/10 repeating
    # pomodoro( tRealBreak ) # 90/15 repeating
    pomodoro( tWorkHardWalkHard ) # 120/20 repeating
    # pomodoro( tLongHaul ) # 120/10 repeating
    
    
