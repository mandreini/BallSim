__author__ = 'Matt'

import numpy
import pygame
import parameters

class Gravity(object):
    def __init__(self, num_bodies):
        self.masses = numpy.ones(num_bodies, dtype=float) * parameters.m0
        self.radii = numpy.ones(num_bodies) * parameters.r0
        self.x_pos_list = numpy.random.rand(num_bodies) * parameters.xmax
        self.y_pos_list = numpy.random.rand(num_bodies) * parameters.ymax
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
        px_dists = parameters.distance(xtab, ytab)
        angles = parameters.get_angle(xtab, ytab)
        m_dists = parameters.px_to_m(px_dists)

        # combine necessary planets and determine (new) masses, remove if necessary
        masses, rem_inds = self.combine(px_dists)
        m1, m2 = numpy.meshgrid(masses, masses)

        if rem_inds is not None:
            m_dists = numpy.delete(m_dists, rem_inds, 0)
            m_dists = numpy.delete(m_dists, rem_inds, 1)
            angles = numpy.delete(angles, rem_inds, 0)
            angles = numpy.delete(angles, rem_inds, 1)

        # compute forces on ball, perform kinematics / numerical integration
        fg = numpy.where(m_dists > 10, parameters.g * m1 * m2 / (m_dists * m_dists), 0)

        ax = fg/m2 * numpy.cos(angles)
        ay = fg/m2 * numpy.sin(angles)
        ax = numpy.sum(ax, axis=1)
        ay = numpy.sum(ay, axis=1)

        self.x_velocities += ax * tstep
        self.y_velocities += ay * tstep

        self.x_pos_list += self.x_velocities * tstep
        self.y_pos_list += self.y_velocities * tstep

        if parameters.bounce:
            # bounces on edge of the screen
            self.x_velocities = numpy.where((self.x_pos_list < 0) | (self.x_pos_list > parameters.xmax),
                                            -self.x_velocities, self.x_velocities)
            self.y_velocities = numpy.where((self.y_pos_list < 0) | (self.y_pos_list > parameters.ymax),
                                            -self.y_velocities, self.y_velocities)

        else:
            # wrap-around planets off-screen (move's to other side of screen)
            self.x_pos_list = numpy.where(self.x_pos_list < 0, parameters.xmax, self.x_pos_list)
            self.x_pos_list = numpy.where(self.x_pos_list > parameters.xmax, 0, self.x_pos_list)
            self.y_pos_list = numpy.where(self.y_pos_list < 0, parameters.ymax, self.y_pos_list)
            self.y_pos_list = numpy.where(self.y_pos_list > parameters.ymax, 0, self.y_pos_list)

    def combine(self, dists):
        """
        Combines planets where necessary: deletes lower-indexed planet, doubles mass of higher indexed planet
        :param dists: ndarray - numpy array of distances between planets
        :return: ndarray, ndarray - masses array, to_delete index array
        """
        curr_masses = self.masses
        close_inds1, close_inds2 = numpy.where((dists != 0) & (dists < self.radii/3.))

        if len(close_inds1):
            close_masses = curr_masses[close_inds1]
            to_increase = numpy.where(close_masses == numpy.max(close_masses))[0]
            if len(to_increase) > 1: to_increase = to_increase[0]
            to_del = numpy.ma.array(close_inds1, mask=False)
            to_del.mask[to_increase] = True
            to_del = to_del.compressed()
            if len(to_del) == 0:
                to_del = close_inds1

            curr_masses[to_increase] += numpy.sum(self.masses[to_del])
            self.increase_size(to_increase, to_del)
            self.new_velocity(to_increase, to_del)
            self.destroy(to_del)
            curr_masses = numpy.delete(curr_masses, to_del)
            return curr_masses, to_del

        return curr_masses, None

    def increase_size(self, keep_planet, del_planets):
        """
        Increases radius based on area so A_new = A1 + A2 + ...
        :param keep_planet: array-like - index of the planet to remain
        :param del_planets: index of the planets to be deleted
        """
        keep_area = parameters.area(self.radii[keep_planet])
        del_area = parameters.area(self.radii[del_planets])
        new_area = keep_area + numpy.sum(del_area)
        self.radii[keep_planet] = parameters.radius(new_area)

    def new_velocity(self, keep_planet, del_planets):
        """
        Computes the resulting (momentum) velocity when worlds collide
        :param keep_planet: array-like - index of the planet to remain
        :param del_planets: array-like - index of the planets to be deleted
        """
        mass_keep = self.masses[keep_planet]
        mass_del = self.masses[del_planets]
        vx_keep, vx_del = self.x_velocities[keep_planet], self.x_velocities[del_planets]
        vy_keep, vy_del = self.y_velocities[keep_planet], self.y_velocities[del_planets]

        vrx = (mass_keep*vx_keep + numpy.sum(mass_del*vx_del)) / (mass_keep + numpy.sum(mass_del))
        vry = (mass_keep*vy_keep + numpy.sum(mass_del*vy_del)) / (mass_keep + numpy.sum(mass_del))

        self.x_velocities[keep_planet] = vrx
        self.y_velocities[keep_planet] = vry

    def draw(self, scr, img):
        """ Draws all the objects in Gravity
        :param scr: pygame.Surface - screen to draw on
        :param img: pygame.Surface - image to draw
        """

        xpositions = self.x_pos_list.astype(int)
        ypositions = self.y_pos_list.astype(int)
        sizes = self.radii

        for i in range(len(xpositions)):
            ballimg2 = parameters.scale(img, int((sizes[i])))
            bodyrect = ballimg2.get_rect()
            bodyrect.center = (xpositions[i], ypositions[i])
            scr.blit(ballimg2, bodyrect)

    def destroy(self, ind):
        """
        Removes a planet 'object' from the arrays
        :param ind: the index to delete
        """
        self.radii = numpy.delete(self.radii, ind)
        self.masses = numpy.delete(self.masses, ind)
        self.x_pos_list = numpy.delete(self.x_pos_list, ind)
        self.y_pos_list = numpy.delete(self.y_pos_list, ind)
        self.x_velocities = numpy.delete(self.x_velocities, ind)
        self.y_velocities = numpy.delete(self.y_velocities, ind)

    def create_planet(self, x, y, mass):
        """
        Creates a planet at a given location with a given mass
        :param x: int - x location (pixels)
        :param y: int - y location (pixels)
        :param mass: number - mass of planet
        """
        self.radii = numpy.append(self.radii, 25)
        self.masses = numpy.append(self.masses, mass)
        self.x_pos_list = numpy.append(self.x_pos_list, x)
        self.y_pos_list = numpy.append(self.y_pos_list, y)
        self.x_velocities = numpy.append(self.x_velocities, 0)
        self.y_velocities = numpy.append(self.y_velocities, 0)