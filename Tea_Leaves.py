# James Watson, 2025-07: Silly little program for depicting the mood of the day

from turtle import setup, pendown, penup, pensize, forward, right, left, speed, bgcolor, goto, pencolor, done, hideturtle, title
from random import random, choice

import numpy as np

## Drawing Params ##
_COLR_MIN = 124/255.0
_COLR_MAX = 255/255.0
_PROB_MIN = 0.0625
_PROB_MAX = 0.5000



def sample_vec_normal_int( center, scale ):
    """ Sample independent normal coordinates """
    Ndim      = len( center )
    rtnCoords = [0 for _ in range(Ndim)]
    for i in range( Ndim ):
        rtnCoords[i] = int( np.random.normal( center[i], scale[i] ) )
    return rtnCoords


def sample_box_normal_int( bbox ):
    """ Sample independent normal coordinates in a boudning box """
    bbox   = np.array( bbox )
    N      = bbox.shape[1]
    center = [0 for _ in range(N)]
    scale  = [0 for _ in range(N)]
    for i in range(N):
        center[i] = (bbox[1,i] + bbox[0,i])/2.0
        scale[i]  = abs(bbox[1,i] - bbox[0,i])/3.5
    return sample_vec_normal_int( center, scale )


def choose_int_range( lo, hi ):
    """ Randomly choose an int on [`lo`, `hi`], inclusive """
    return choice( list( range( int( lo ), int( hi+1 ) ) ) )


def randf( lo, hi ):
    """ Randomly choose a float on [`lo`, `hi`], inclusive """
    span = hi - lo
    return lo + span*random()


def draw_random_ideogram( bbox ):
    """ Draw a diagram according to the above settings """
    _SCALE    = np.linalg.norm( np.subtract( bbox[1], bbox[0] ) )
    ## Drawing Params ##
    _SIZE_MIN = choose_int_range( 1, 3 )
    _SIZE_MAX = choose_int_range( _SIZE_MIN+1, _SIZE_MIN+9 )
    _LINE_MIN =  _SCALE / 50.0
    _LINE_MAX =  _SCALE /  5.0
    _TURN_MIN = randf(  5.0,  50.0 )  
    _TURN_MAX = randf( 90.0, 170.0 )  
    ## Drawing Probabilities ##
    _PROB_SIZ = randf( _PROB_MIN, _PROB_MAX )
    _PROB_PEN = randf( _PROB_MIN, _PROB_MAX )
    _PROB_BRK = randf( 1.0/50, 1.0/40 )
    goto( sample_box_normal_int( bbox ) )
    down = True
    pendown()
    pencolor( 
        randf( _COLR_MIN, _COLR_MAX ),
        randf( _COLR_MIN, _COLR_MAX ),
        randf( _COLR_MIN, _COLR_MAX )
    )
    while random() > _PROB_BRK:
        if random() < _PROB_PEN:
            penup()
            down = False
            goto( sample_box_normal_int( bbox ) )
        else:
            if random() < _PROB_SIZ:
                pensize( choose_int_range( _SIZE_MIN, _SIZE_MAX ) )
            forward( randf( _LINE_MIN, _LINE_MAX ) )
            if random() < 0.5:
                left( randf( _TURN_MIN, _TURN_MAX ) )
            else:
                right( randf( _TURN_MIN, _TURN_MAX ) )
        if not down:
            pendown()
            down = True
    penup()

########## MAIN ####################################################################################
if __name__ == "__main__":
    dim = np.array([1000,1000,])
    div = 4
    stp = dim / div
    setup( dim[0], dim[1] )
    title( "Virtual Tea Leaves" )
    bgcolor( "black" )
    speed(10)
    for i in range( div ):
        xBgn = int( i*stp[0]-dim[0]/2.0 )
        xEnd = int( xBgn+stp[0] )
        for j in range( div ):
            yBgn = int( j*stp[1]-dim[1]/2.0 )
            yEnd = int( yBgn+stp[1] )
            draw_random_ideogram( [[xBgn,yBgn,],[xEnd,yEnd,]] )
    hideturtle()
    done()