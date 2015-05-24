__author__ = 'Matt'

import bisect
import numpy
import pygame

# simulation constants
xmax = 800
ymax = 600
num_planets = 150.0
bounce = True
g = 6.67e-11
m0 = 1.e24
d0 = 25
mouse_mass = 10e10
arr_height = 22
arr_base = 35
box_height = 60
box_width = 120

# colors
white          = (255, 255, 255)
black          = (  0,   0,   0)
grey           = (160, 160, 160)
red            = (255,   0,   0)
green          = (  0, 255,   0)
blue           = (  0,   0, 255)
yellow         = (255, 255,   0)
purple         = (255,   0, 255)
cyan           = (  0, 255, 255)

# pygame Font objects
pygame.font.init()
p_count_font = pygame.font.SysFont("cambria", 30)
menu_font = pygame.font.SysFont("miriam", 18)
opt_font = pygame.font.SysFont("miriam", 18)
title_font = pygame.font.SysFont("monotone", 80)
start_font = pygame.font.SysFont("miriam", 50)

# pygame Surface image(s)
ballimg = pygame.image.load("images/spherical.gif")
imgsizes = [25, 50, 100]
ballimgs = [pygame.transform.scale(ballimg, (s, s)) for s in imgsizes]

startimg = pygame.image.load("images/start_button.gif")
startimg = pygame.transform.scale(startimg, (550, 100))

toggleimg = pygame.image.load("images/toggle_button.gif")
toggleimg = pygame.transform.scale(toggleimg, (100, 50))

# lambda functions
px_to_m = lambda px: px * 1e5
distance = lambda x, y: numpy.sqrt(x * x + y * y)
get_angle = lambda x, y: numpy.arctan2(y, x)
scale = lambda img, size: pygame.transform.scale(img, (size, size))
area = lambda r: numpy.pi*r*r
radius = lambda A: numpy.sqrt(A / numpy.pi)
image = lambda size: ballimgs[bisect.bisect(imgsizes, size) - 1]