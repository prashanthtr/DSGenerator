
import math
import numpy as np

def sine(val):
    return math.sin(val)

def triangle(ind, period):
    return 2*abs(ind/period - math.floor(ind/period + 0.5))

def sawtooth(ind, period, cutoff):
    return 2*abs(ind/period - math.floor(ind/period + cutoff))