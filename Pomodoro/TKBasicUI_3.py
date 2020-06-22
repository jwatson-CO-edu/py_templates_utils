#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Template Version: 2020-02-07

__progname__ = "TKBasicUI_3.py"
__author__   = "James Watson"
__version__  = "2020.05"
__desc__     = "Template tk class"

"""  
~~~ DEV PLAN ~~~
[Y] Test `TKBasicApp` - 2020-05-19: Tested, works as intended
"""

# === Init Environment =====================================================================================================================
# ~~~ Prepare Paths ~~~
import sys, os.path
SOURCEDIR = os.path.dirname( os.path.abspath( __file__ ) ) # URL, dir containing source file: http://stackoverflow.com/a/7783326
PARENTDIR = os.path.dirname( SOURCEDIR )
sys.path.insert( 0 , PARENTDIR ) # Might need this to fetch a lib in a parent directory

# ~~~ Imports ~~~
# ~~ Standard ~~
import time
from math import pi , sqrt
from tkinter import Tk , Frame , Canvas # Standard Python cross-platform GUI
# ~~ Special ~~
import numpy as np
# ~~ Local ~~
from Timing import HeartRate

# ___ End Init _____________________________________________________________________________________________________________________________

# === TKinter Classes ===

# == class TKBasicApp ==
            
class TKBasicApp:
    """ TKinter application GUI """
    # Modeled after https://stackoverflow.com/a/29158947
    
    def __init__( self , winWidth , winHeight , engineHz = 30 , title = "DEFAULT WINDOW TITLE" ,
                  engineFuncs = [] , setupFuncs = [] ):
        """  """
        
        # 1. Init Tkinter root
        self.rootWin   = Tk() # ---------------- Main window for Tk controls
        self.winWidth  = winWidth # ------------ Width of the main window
        self.winHeight = winHeight # ----------- Height of the main window
        self.panel     = None # ---------------- Container for (most) controls
        self.engine    = None # ---------------- List of functions that does work of the app
        self.governor  = HeartRate( engineHz ) # Maintains engine update rate
        self.set_title( title ) # -------------- Set window title
        self.set_engine_funcs( *engineFuncs )
        self.set_gui_funcs( *setupFuncs )
        
    def set_engine_funcs( self , *engineFuncs ):
        # 2. Init Engine
        if len( engineFuncs ) > 0: # If functions were provided, then copy the list
            self.engine = engineFuncs[:]
        else: # Else no funcs provided, create a list with a single dummy function
            self.engine = [ self.default_engine_func ] # There's no side effect to appending to this
            
    def set_gui_funcs( self , *setupFuncs ):
        # 3. Init GUI list
        if len( setupFuncs ) > 0:
            self.GUIconstructor = setupFuncs[:]
        else:
            self.GUIconstructor = [ self.default_frame ]
        
    def set_title( self , winTitle ):
        """ Set the title for the Tkinter window """
        self.rootWin.wm_title( str( winTitle ) )
        
    def default_frame( self ):
        """ Create a panel to contain all the controls """
        self.panel = Frame( self.rootWin , width = self.winWidth , height = self.winHeight )
        self.panel.pack()
    
    def add_engine_functions( self , *funcs ):
        """ Add one or more functions to the engine update """
        self.engine.extend( funcs )
    
    def run_engine( self ):
        """ Run engine functions, then wait for remaining time, and Repeat periodically """
        # 1. Execute each of the engine functions, in turn
        for f in self.engine:
            f()
        # 2. Ask for this function to be called again in the future, and reset the cycle beginning
        self.rootWin.after( int( self.governor.get_remainder() * 1000 ) , self.run_engine )
        self.governor.mark_time()
    
    def start( self ):
        """ Start app engine, Then the GUI """
        # 1. Populate and pack the GUI
        for g in self.GUIconstructor:
            g()
        # 2. Start the app engine
        self.run_engine()
        # 3. Mainloop
        self.rootWin.mainloop()
        
    def default_engine_func( self ):
        """ Do-nothing update! """
        pass
    
    def default_frame( self ):
        """ Simplest GUI window possible """
        self.panel = Frame( self.rootWin ,  # A panel to hold the controls, has its own packing environment
                            width = self.winWidth , height = self.winHeight )
        self.panel.pack() # Remember to pack the control panel!
        print( "Created the default panel!" )
    
# __ End TKBasicApp __

# ___ End TKinter ___

# === Main Program =========================================================================================================================

if __name__ == "__main__":
    print( __progname__  , 'by' , __author__ , ', Version:' , __version__ )
    termArgs = sys.argv[1:] # Terminal arguments , if they exist
    
    if 0:
        app = TKBasicApp( 400 , 300 )
        app.start()
    else:
        
        class Ball:
            def __init__(self, canvas, color):
                self.canvas = canvas
                self.id = canvas.create_oval(10, 10, 25, 25, fill=color)
                self.canvas.move(self.id, 245, 100)

                self.canvas.bind("<Button-1>", self.canvas_onclick)
                self.text_id = self.canvas.create_text(300, 200, anchor='se')
                self.canvas.itemconfig(self.text_id, text='hello')

            def canvas_onclick(self, event):
                self.canvas.itemconfig(
                    self.text_id, 
                    text="You clicked at ({}, {})".format(event.x, event.y)
                )

            def draw( self ):
                self.canvas.move(self.id, 1, 1)
    
        app = TKBasicApp( 500 , 400 , engineHz = 30 , title = "BALL" )
        
        canvas = Canvas( app.rootWin , width=500, height=400, bd=0, highlightthickness=0)
        def make_canvas():
            canvas.pack()
        ball = Ball(canvas, "blue")
        
        app.set_gui_funcs( make_canvas )
        app.set_engine_funcs( ball.draw )
        
        app.start()
        

# ___ End Main _____________________________________________________________________________________________________________________________