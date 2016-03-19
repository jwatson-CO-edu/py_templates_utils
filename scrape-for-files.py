# -*- coding: utf-8 -*-
"""
scrape-for-files.py , Built on Spyder for Python 2.7
James Watson, 2016 February
I left myself a bunch of instructions for how to do things, but they are spread all over!

  == NOTES ==
* Script assumes that it is in the root directory to be searched
"""


# == Init Environment ==

# ~ PATH Changes ~ 
def localize(): # For some reason this is needed in Windows 10 Spyder (Py 2.7)
    """ Add the current directory to Python path if it is not already there """
    from sys import path # I know it is bad style to load modules in function
    import os.path as os_path
    containerDir = os_path.dirname(__file__)
    if containerDir not in path:
        path.append( containerDir )

localize() # You can now load local modules!

# ~ Standard Libraries ~
import math
from math import sqrt, ceil, sin, cos, tan, atan2, radians
from os import linesep
import os.path as os_path
import os
import shutil
# ~ Special Libraries ~
import matplotlib.pyplot as plt
import numpy as np
# ~~ Constants , Shortcuts , Aliases ~~
EPSILON = 1e-7
infty = 1e309 # URL: http://stackoverflow.com/questions/1628026/python-infinity-any-caveats#comment31860436_1628026
endl = linesep

# ~ Helper Functions ~

def eq(op1, op2):
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON
    
def sep(title = ""):
    """ Print a separating title card for debug """
    LINE = '======'
    print LINE + ' ' + title + ' ' + LINE

# == End Init ==

copyList = []

# URL, Traversing Directories: http://pythoncentral.io/how-to-traverse-a-directory-tree-in-python-guide-to-os-walk/
containerDir = os_path.dirname(__file__) # get the containing folder
topLevel = os_path.dirname(containerDir) # get the root folder 
for dirName, subdirList, fileList in os.walk(topLevel):
    #print('Found directory: %s' % dirName)
    if dirName != containerDir:
        #print "At container"
        for fname in fileList:
            if fname[-3:] == 'txt':
                print '\t{}'.format(fname),' --in--> ',dirName
                copyList.append( (os_path.join(dirName, fname) , containerDir) )
                
for srcDestPair in copyList:
    shutil.copy2( srcDestPair[0], srcDestPair[1] )