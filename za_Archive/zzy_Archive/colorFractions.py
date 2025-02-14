#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2016-06-22

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
colorFractions.py , Built on Geany for Python 2.7
James Watson, 2016 June
For defining colors in LaTeX
"""

colorInts = []
colorNames = ['r','g','b']
for color in colorNames:
    colorInts.append( float( raw_input(color + ' as int: ') ) )
prntStr = '{ '
for color in colorInts:
    prntStr += "{0:.2f}".format( color / 255 ) + " , "
    
prntStr = prntStr[:-2] + "}"
print prntStr