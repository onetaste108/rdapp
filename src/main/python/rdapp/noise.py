from opensimplex import OpenSimplex
import numpy as np
noise = OpenSimplex()

def s1(x=0, y=0):
    return noise.noise2d(x, y)

def s2(x=0, y=0):
    return np.float32([
        noise.noise2d(x, y),
        noise.noise2d(x, y+100)
    ])

def s3(x=0, y=0):
    return np.float32([
        noise.noise2d(x, y),
        noise.noise2d(x, y+100),
        noise.noise2d(x, y+200)
    ])
