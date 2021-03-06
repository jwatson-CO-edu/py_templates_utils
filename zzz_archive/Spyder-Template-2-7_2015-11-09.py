# -*- coding: utf-8 -*-
"""
FILENAME.py , Built on Spyder for Python 2.7
James Watson, YYYY MONTHNAME
A ONE LINE DESCRIPTION OF THE FILE

"""
# == Init Environment ==

# Standard Libraries
import math
from math import sqrt, ceil
# Special Libraries
import matplotlib.pyplot as plt
import numpy as np
# == Constants ==
EPSILON = 1e-7

def localize():
    """ Add the current directory to Python path if it is not already there """
    from sys import path # I know it is bad style to load modules in function
    containerDir = os.path.dirname(__file__)
    if containerDir not in path:
        path.append( containerDir )

localize() # You can now load local modules!

# = Helper Functions =

def eq(op1, op2):
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON

# = End Helper =

# == End Init ==


