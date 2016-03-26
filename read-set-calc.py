# -*- coding: utf-8 -*-
"""
ready-set-calc.py , Built on Spyder for Python 2.7
James Watson, 2015 December
Run this file to use Spyder as a calculator

  == LOG ==
2016-03-26: Wrote 'degrees' versions of trig functions

  == TODO ==
* 

"""
# == Init Environment ==

# ~ PATH Changes ~ 
def localize():
    """ Add the current directory to Python path if it is not already there """
    from sys import path # I know it is bad style to load modules in function
    import os.path as os_path
    containerDir = os_path.dirname(__file__)
    if containerDir not in path:
        path.append( containerDir )

localize() # You can now load local modules!

# ~ Standard Libraries ~
import math, os
from math import sqrt, ceil, sin, cos, tan, atan2, asin, acos, atan, pi, degrees, radians, log, log10, exp, e, factorial
# ~ Special Libraries ~
import matplotlib.pyplot as plt
import numpy as np
# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl = os.linesep
SOURCEDIR = os.path.dirname(os.path.abspath(__file__)) # URL, dir containing source file: http://stackoverflow.com/a/7783326

# ~ Helper Functions ~

def eq(op1, op2):
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON

# == End Init ==


# == Statistics and Combinatorics ==

def nCr(n,r):
    """ Number of combinations for 'n' Choose 'r' """
    return factorial(n) / ( factorial(r) * factorial(n-r) )

# == End Statistics ==


# == Trigonometry ==
# = Trig in Degrees =
def cosd(angleDeg):
    """ Return the cosine of the angle specified in degrees """
    return cos( radians( angleDeg ) )

def sind(angleDeg):
    """ Return the sine of the angle specified in degrees """
    return sin( radians( angleDeg ) )

def tand(angleDeg):
    """ Return the tangent of the angle specified in degrees """
    return tan( radians( angleDeg ) )
    
def atan2d( y , x ):
    """ Return the angle, in degrees, of a vector/phasor specified by 'y' and 'x' """
    return degrees( atan2( y , x) )
    
def asind( ratio ):
    """ Return the arcsine of a ratio, degrees """
    return degrees( asin( ratio ) ) 
    
def acosd( ratio ):
    """ Return the arccosine of a ratio, degrees """
    return degrees( acos( ratio ) )
    
def atand( ratio ):
    """ Return the arctangent of a ratio, degrees """
    return degrees( atan( ratio ) )
# = End Deg Trig =
# == End Trig ==