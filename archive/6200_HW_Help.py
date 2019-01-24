# -*- coding: utf-8 -*-
"""
6200_HW_Help.py , Built on Spyder for Python 2.7
James Watson, 2015 October
Helpful functions to expedite ME EN 6200 HW

== NOTES ==
* Vanilla Python knows how to handle complex numbers!

== TODO ==
* System: Add the facility to compute poles and zeros from terms expressed as lists
"""

# Standard Libraries
import math
from math import sqrt, ceil, degrees, pi
from os import linesep as endl
# Special Libraries
import matplotlib.pyplot as plt
import numpy as np
# == Constants ==
EPSILON = 1e-5

# == Helper Functions ==

def eq(op1, op2):
    """ Return true if op1 and op2 are close enough """
    return abs(op1 - op2) <= EPSILON

# == End Helper ==

# == Time-Domain Specifications ==

def Mp_to_zeta(Mp):
    return ( -1 * math.log(Mp) ) / math.sqrt( math.pi ** 2 + math.log(Mp) ** 2)

def __zeta_to_theta(zeta):
    temp = math.asin(zeta)
    return [temp, math.degrees(temp)]

def zeta_to_theta(zeta):
    temp = __zeta_to_theta(zeta)
    print("{0:.3f} rad , {1:.3f} deg".format(temp[0],temp[1]))
    return temp

def Mp_to_theta(Mp):
    zeta = Mp_to_zeta(Mp)
    temp = __zeta_to_theta(zeta)
    print( "zeta: {0:.3} , {1:.3f} rad , {2:.3f} deg".format(zeta,temp[0],temp[1]) ) # format to 3 decimals
    return temp

print("Time domain specs loaded!")

# == End Specifications ==

# == Root Finders ==

def quad(a,b,c):
    """ Return roots of quadratic function a * (x ** 2) + b * (x) + c """
    return np.roots([a,b,c])
    
def coef_to_omega(coefs):
    rts = np.roots(coefs)
    omega_n = np.absolute(rts)
    #phase = np.angle(rts)
    zeta = []
    omega_d = []
    for i in range(len(rts)):
        zeta.append(abs(np.real(rts[i])/omega_n[i]))
        omega_d.append(omega_n[i] * math.sqrt(1 - zeta[i] ** 2))
        
        print( ("root: {0:.3} , zeta: {1:.3f} ," + endl + "omega_n: {2:.3f} , omega_d: {3:.3f}" + endl) \
        .format(rts[i], zeta[i], omega_n[i], omega_d[i]) )

# == class System ==
# Transfer Function with some root locus facilities

class System(object):
    """ Represents a transfer function with poles and zeros as follows
    zeros: [ sigma+(omega)j , sigma+(omega)j , ... ]
    poles: [ sigma+(omega)j , sigma+(omega)j , ... ] """
    def __init__(self, zeros, poles):
        self.zeros = zeros
        self.poles = poles
        self.n = len(self.poles)
        self.m = len(self.zeros)
        
    def angles_to_point(self, point, prt = False):
        """ Return the sum of angles from poles and zeros to point """
        angleSum = 0
        for pole in self.poles:
            temp = degrees(np.angle(pole - point))
            if prt:
                print temp
            angleSum += temp
        for zero in self.zeros:
            temp = degrees(np.angle(zero - point))
            if prt:
                print temp
            angleSum += temp
        return angleSum
        
    def angle_condition(self, point):
        """ Return true if 'point' satisfies the angle condition for root locus """
        k = len(self.zeros) + len(self.poles)
        return eq(180.0*(2*k), self.angles_to_point(point, True))
        
    def centroid(self):
        """ Compute the centroid on the real axis.
        This function assumes poles and zeros are open loop """
        poleSum = 0
        zeroSum = 0
        for pole in self.poles:
            poleSum += pole
        for zero in self.zeros:
            zeroSum += zero
        return (poleSum - zeroSum) / (self.n - self.m)
        
        
    def K_graph_method(self, point):
        """ Use the graphical method to find the K associated s = point, 
        sigma+(omega)j 
        This function assumes poles and zeros are open loop
        This function assumes 'point' is known to be on the root locus """
        if not self.angle_condition(point):
            print "The angle condition is NOT met at point " + str(point) + " , " + str(self.angles_to_point(point))
        poleProduct = 1
        zeroProduct = 1
        for pole in self.poles:
            poleProduct *= np.absolute((point) - (pole))
        for zero in self.zeros:
            zeroProduct *= np.absolute((point) - (zero))
        return poleProduct/zeroProduct

# == End System ==
    
print("Roots loaded!")
    
# == End Roots ==


# == Abandoned Code ==

#def quad(a,b,c):
#    roots = []
#    d = b ** 2 - 4 * a * c
#    if d > 0:
#        roots.append( (-1 * b + math.sqrt(d))/ (2 * a) )
#        roots.append( (-1 * b - math.sqrt(d))/ (2 * a) )
#    elif d == 0:
#        roots.append( (-1 * b) / (2 * a ) )
#    else:
#        real = (-1 * b) / ( 2 * a )
#        im = math.sqrt(abs(d)) / (2 * a)
#        roots.append( str( real ) + ' + ' + str( im ) + 'j' )
#        roots.append( str( real ) + ' - ' + str( im ) + 'j' )
#    for root in roots:
#        print( str( root ) + '\n' )
#    return roots

# == End Abandoned ==