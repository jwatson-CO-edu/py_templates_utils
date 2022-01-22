"""
https://www.geeksforgeeks.org/how-to-create-a-countdown-timer-using-python/
https://stackoverflow.com/a/16573339
"""
########## INIT & SETTINGS #############################################################################################


##### Imports #####
import os, time, curses


##### Schedule #####
tProgram = [
    ( 55 * 60, "Work"  ),
    (  5 * 60, "Break" ),
    ( 55 * 60, "Work"  ),
    (  5 * 60, "Break" ),
    ( 55 * 60, "Work"  ),
    ( 15 * 60, "Long Break" ),
]

##### Settings #####
duration =   1 # ----- Duration of tone [s]
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
    
    def clean():
        """ Return terminal to normal """
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
    
    # Draw Static Portion #
    stdscr.border(0)
    stdscr.addstr(5, 5, 'Pomodoro Timer', curses.A_BOLD)
    stdscr.addstr(6, 5, '[Space]: Pause, [n]: Next Interval, [r]: Restart Interval, [q]: Quit', curses.A_NORMAL)
    
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
                timer += f"{mins:02}:{secs:02}"
                t -= 1
            # 4. Else timer is paused, display remaining but do not decrement it
            else:
                timer += f"PAUSED AT {mins:02}:{secs:02}"
                
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
    pomodoro( tProgram )
    
