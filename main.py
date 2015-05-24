__author__ = 'Matthew Andreini'

import numpy
import pygame
import gravity
import parameters
import menu

pygame.init()

# set up screen
reso = (parameters.xmax, parameters.ymax)
scr = pygame.display.set_mode(reso)

# menu object
main_menu = menu.Menu()

# game loop
t0 = pygame.time.get_ticks() * 0.001
running = True
in_menu = True
mdown = False

while running:
    t = pygame.time.get_ticks() * 0.001
    dt = t - t0
    t0 = t

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mdown = True
        if event.type == pygame.MOUSEBUTTONUP:
            pass

    keys = pygame.key.get_pressed()
    mousepos = pygame.mouse.get_pos()

    if keys[pygame.K_ESCAPE]:
        running = False
    if keys[pygame.K_p]:
        dt = 0  # 'pause'

    if in_menu:
        in_menu = not main_menu.draw(scr, mousepos, mdown)
        if not in_menu:
            galaxy = gravity.Gravity(main_menu.edge_toggle[0], main_menu.values)
    else:
        if keys[pygame.K_RIGHT]: galaxy.x_pos_list -= 1
        if keys[pygame.K_LEFT]: galaxy.x_pos_list += 1
        if keys[pygame.K_UP]: galaxy.y_pos_list += 1
        if keys[pygame.K_DOWN]: galaxy.y_pos_list -= 1

        in_menu = keys[pygame.K_m]

        galaxy.get_forces(dt)
        galaxy.draw(scr)

    mdown = False  # replace with better "on click" option
    pygame.event.pump()
    pygame.display.flip()

pygame.quit()