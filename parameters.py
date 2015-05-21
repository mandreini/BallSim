__author__ = 'Matt'

import numpy
import pygame

xmax = 800
ymax = 600
num_planets = 150
bounce = True
g = 6.67e-11
m0 = 1.e24
r0 = 25
mouse_mass = 10e10

px_to_m = lambda px: px * 1e5
distance = lambda x, y: numpy.sqrt(x * x + y * y)
get_angle = lambda x, y: numpy.arctan2(y, x)
scale = lambda img, size: pygame.transform.scale(img, (size, size))
area = lambda r: numpy.pi*r*r
radius = lambda A: numpy.sqrt(A / numpy.pi)