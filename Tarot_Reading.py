# James Watson, 2025-07: Silly little program for depicting the mood of the day

from turtle import screensize, pendown, penup, pensize, forward, right, left, speed, bgcolor
## Drawing Params ##
_SIZE_MIN =   2
_SIZE_MAX =   6
_LINE_MIN =  50
_LINE_MAX = 250
_TURN_MIN =   5
_TURN_MAX = 175
_COLR_MIN = 124
_COLR_MAX = 255
## Drawing Probabilities ##
_PROB_SIZ = 0.25
_PROB_PEN = 0.25
_PROB_BRK = 1.0/15