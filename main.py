__author__ = 'Matthew Andreini'

import numpy
import pygame
import gravity
import parameters

pygame.init()

# set up screen
reso = (parameters.xmax, parameters.ymax)
scr = pygame.display.set_mode(reso)

# sim object
galaxy = gravity.Gravity(parameters.num_planets)

# image
ballimg = pygame.image.load("spherical.gif")
ballimg = pygame.transform.scale(ballimg, (25,25))
ballrect = ballimg.get_rect()

# game loop
t0 = pygame.time.get_ticks() * 0.001
running = True

while running:
    t = pygame.time.get_ticks() * 0.001
    dt = t - t0
    t0 = t

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mousex, mousey = pygame.mouse.get_pos()
            galaxy.create_planet(mousex, mousey, parameters.mouse_mass)

        if event.type == pygame.MOUSEBUTTONUP:
            mouse_planet_ind = numpy.where(galaxy.masses == parameters.mouse_mass)
            if len(mouse_planet_ind):
                galaxy.destroy(mouse_planet_ind)

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False
    if keys[pygame.K_p]:
        dt = 0  # 'pause'

    if keys[pygame.K_RIGHT]: galaxy.x_pos_list -= 1
    if keys[pygame.K_LEFT]: galaxy.x_pos_list += 1
    if keys[pygame.K_UP]: galaxy.y_pos_list += 1
    if keys[pygame.K_DOWN]: galaxy.y_pos_list -= 1

    scr.fill((0, 0, 0))
    galaxy.get_forces(dt)
    galaxy.draw(scr, ballimg)

    pygame.event.pump()
    pygame.display.flip()

pygame.quit()