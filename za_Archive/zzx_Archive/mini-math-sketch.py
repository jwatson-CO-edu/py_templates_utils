#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division

# === Init Env ===
import math
from math import sqrt , pi , degrees , radians , e , exp , sqrt , factorial , log , sin , cos , tan
from math import log as ln
from random import random , randrange
import numpy as np

# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7 # Margin for equality
infty = 1e309 # Python representation of infinity
import os
endl = os.linesep # OS-specific newline

# === End Init ===

# == Math Helpers ==

def eq( op1 , op2 ): 
    """ Return true if op1 and op2 are close enough """ # i.e. to account for floating point rounding errors
    return abs( op1 - op2 ) <= EPSILON
    
def log2( x ): 
    """ Return the log base 2 of 'x' """
    return log( x , 2 )

# == End Helpers ==

# == Application Specific ==================================================================================================================

if __name__ == "__main__":
    pass

# == End Specific ==========================================================================================================================

