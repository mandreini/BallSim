__author__ = 'Matt'

import numpy
import pygame


class Gravity(object):
    def __init__(self, num_bodies):
        self.masses = numpy.ones(num_bodies, dtype=float) * m0
        self.sizes = numpy.ones(num_bodies) * s0
        self.x_pos_list = numpy.random.rand(num_bodies) * xmax
        self.y_pos_list = numpy.random.rand(num_bodies) * ymax
        self.x_velocities = numpy.zeros(num_bodies)
        self.y_velocities = numpy.zeros(num_bodies)

    def get_forces(self, tstep):
        """
        Determines the forces on a planet due to all other planets and updates velocities and positions
        :param tstep: float - time step
        """

        # compute distances from every point to every point in x and y
        xtab1, xtab2 = numpy.meshgrid(self.x_pos_list, self.x_pos_list)
        ytab1, ytab2 = numpy.meshgrid(self.y_pos_list, self.y_pos_list)
        xtab = xtab1 - xtab2
        ytab = ytab1 - ytab2

        # determine resulting distances (and angles) from x,y distances
        px_dists = distance(xtab, ytab)
        angles = get_angle(xtab, ytab)
        m_dists = px_to_m(px_dists)

        # combine necessary planets and determine (new) masses, remove if necessary
        masses, rem_inds = self.combine(px_dists)
        m1, m2 = numpy.meshgrid(masses, masses)

        if rem_inds is not None:
            m_dists = numpy.delete(m_dists, rem_inds, 0)
            m_dists = numpy.delete(m_dists, rem_inds, 1)
            angles = numpy.delete(angles, rem_inds, 0)
            angles = numpy.delete(angles, rem_inds, 1)

        # compute forces on ball, perform kinematics / numerical integration
        fg = numpy.where(m_dists != 0, g * m1 * m2 / (m_dists * m_dists), 0)

        ax = fg/masses * numpy.cos(angles)
        ay = fg/masses * numpy.sin(angles)
        ax = numpy.sum(ax, axis=1)
        ay = numpy.sum(ay, axis=1)

        self.x_velocities += ax*tstep
        self.y_velocities += ay*tstep

        self.x_pos_list += self.x_velocities*tstep
        self.y_pos_list += self.y_velocities*tstep

        if bounce:
            # bounces on edge of the screen
            self.x_velocities = numpy.where((self.x_pos_list < 0) | (self.x_pos_list > xmax),
                                            -self.x_velocities, self.x_velocities)
            self.y_velocities = numpy.where((self.y_pos_list < 0) | (self.y_pos_list > ymax),
                                            -self.y_velocities, self.y_velocities)

        else:
            # wrap-around planets off-screen (move's to other side of screen)
            self.x_pos_list = numpy.where(self.x_pos_list < 0, xmax, self.x_pos_list)
            self.x_pos_list = numpy.where(self.x_pos_list > xmax, 0, self.x_pos_list)
            self.y_pos_list = numpy.where(self.y_pos_list < 0, ymax, self.y_pos_list)
            self.y_pos_list = numpy.where(self.y_pos_list > ymax, 0, self.y_pos_list)

    def combine(self, dists):
        """
        Combines planets where necessary: deletes lower-indexed planet, doubles mass of higher indexed planet
        :param dists: ndarray - numpy array of distances between planets
        :return: ndarray, ndarray - masses array, to_delete index array
        """
        curr_masses = self.masses
        close_inds1, close_inds2 = numpy.where((dists != 0) & (dists < 20))

        if len(close_inds1):
            to_del = close_inds1[0]
            to_increase = close_inds2[0]
            self.sizes[to_increase] *= 2
            self.destroy(to_del)
            curr_masses = numpy.delete(curr_masses, to_del)
            return curr_masses, to_del

        return curr_masses, None

    def draw(self):
        """ Draws all the objects in Gravity """

        xpositions = self.x_pos_list.astype(int)
        ypositions = self.y_pos_list.astype(int)
        sizes = self.sizes

        for i in range(len(xpositions)):
            bodyrect = ballrect
            bodyrect.center = (xpositions[i],ypositions[i])
            # ballimg2 = scale(int(sizes[i]))
            scr.blit(ballimg, bodyrect)

    def destroy(self, ind):
        """
        Removes a planet 'object' from the arrays
        :param ind: the index to delete
        """
        self.masses = numpy.delete(self.masses, ind)
        self.x_pos_list = numpy.delete(self.x_pos_list, ind)
        self.y_pos_list =  numpy.delete(self.y_pos_list, ind)
        self.x_velocities = numpy.delete(self.x_velocities, ind)
        self.y_velocities =  numpy.delete(self.y_velocities, ind)

pygame.init()

# set up screen
xmax = 800
ymax = 600
reso = (xmax, ymax)
scr = pygame.display.set_mode(reso)

# simulation
bounce = False
g = 6.67e-11
m0 = 1.e24
s0 = 25
px_to_m = lambda px: px * 1e5
distance = lambda x, y: numpy.sqrt(x*x + y*y)
get_angle = lambda x, y: numpy.arctan2(y, x)
scale = lambda size: pygame.transform.scale(ballimg, (size, size))

galaxy = Gravity(10)

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

    keys = pygame.key.get_pressed()

    if keys[pygame.K_ESCAPE]:
        running = False

    if keys[pygame.K_RIGHT]:
        galaxy.x_pos_list -= 1
    if keys[pygame.K_LEFT]:
        galaxy.x_pos_list += 1
    if keys[pygame.K_UP]:
        galaxy.y_pos_list += 1
    if keys[pygame.K_DOWN]:
        galaxy.y_pos_list += 1

    scr.fill((0, 0, 0))
    galaxy.get_forces(dt)
    galaxy.draw()

    pygame.event.pump()
    pygame.display.flip()

pygame.quit()