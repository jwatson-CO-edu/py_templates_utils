# -*- coding: utf-8 -*-
"""
ready-set-calc.py , Built on Spyder for Python 2.7
James Watson, 2015 December
Run this file to use Spyder as a calculator

  == TODO ==
* Write 'degrees' versions of trig functions

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
import math
from math import sqrt, ceil, sin, cos, tan, atan2, asin, acos, atan, pi, degrees, radians
# ~ Special Libraries ~
import matplotlib.pyplot as plt
import numpy as np
# ~ Constants ~
EPSILON = 1e-7

# ~ Helper Functions ~

def eq(op1, op2):
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON

# == End Init ==



