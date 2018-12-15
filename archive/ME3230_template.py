#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Template Version: 2018-02-11

# ~~ Future First ~~
from __future__ import division # Future imports must be called before everything else, including triple-quote docs!

"""
ME3230_template.py , Built on Wing 101 for Python 2.7
James Watson, YYYY MONTHNAME
Helpful functions for grading 3230 , Lab NN
"""

# === Init Environment =====================================================================================================================
from math import pi , sqrt # ------- Math functions
from decimal import Decimal # Fromattingg decimal numbers
# ___ End Init _____________________________________________________________________________________________________________________________

# == Helper Functions ==

def bin_2_dec( binStr ):
    """ Convert a binary string to a decimal integer """
    return int( binStr , 2 )

def format_e( n ):
    """ URL , Return a string that is number 'n' expressed in scientific notation: https://stackoverflow.com/a/6913576 """
    a = '%E' % Decimal( n )
    return a.split('E')[0].rstrip('0').rstrip('.') + 'E' + a.split('E')[1]

def flatten_nested_sequence( multiSeq ):
    """ Flatten a sequence of sequences ( list or tuple ) into a single , flat sequence of the same type as 'multiSeq' """
    masterList = []
    def flatten_recur( multLst , masterList ):
        """ Does the recursive work of 'flatten_nested_lists' """
        for elem in multLst:
            if isinstance( elem , list ):
                flatten_recur( elem , masterList )
            else:
                masterList.append( elem )
    flatten_recur( multiSeq , masterList )
    if isinstance( multiSeq , tuple ):
        return tuple( masterList )
    else:
        return masterList
    
def Hz_to_radS( freqHz ):
    """ Convert Hz to rad/s """
    return freqHz * 2 * pi

# __ End Helper __

# == Class Constants ==

R_TYPICAL = [ [ 1.0 * mag , 2.0 * mag , 1.6 * mag , 2.2 * mag , 3.3 * mag , 4.7 * mag , 5.6 * mag , 6.8 * mag , 10.0 * mag ] \
              for mag in [ 10**i for i in range(1,6) ] ]
R_TYPICAL = flatten_nested_sequence( R_TYPICAL )
C_TYPICAL = [ 1e-6 , 1e-9 , 10e-9 , 100e-9 , 330e-9 ]

# __ End Constants __


# === Assignment Specific ==================================================================================================================



# ___ End Specific _________________________________________________________________________________________________________________________