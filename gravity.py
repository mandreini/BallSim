__author__ = 'Matt'

import numpy
import pygame
import parameters

class Gravity(object):
    def __init__(self, edge_type, initial_vals):
        self.edge_type = edge_type
        num_bodies = initial_vals[0]
        v_dif = initial_vals[1] * 10
        size_dif = initial_vals[2]

        diams = parameters.d0 + (numpy.random.normal(0, size_dif, num_bodies) * (size_dif - 1)/5)
        self.diams = numpy.where(diams > 0, diams, numpy.abs(diams))
        self.masses = self.diams / parameters.d0 * parameters.m0
        self.x_velocities = numpy.random.normal(0, v_dif+1, num_bodies) * v_dif
        self.y_velocities = numpy.random.normal(0, v_dif+1, num_bodies) * v_dif
        self.x_pos_list = numpy.random.rand(num_bodies) * parameters.xmax
        self.y_pos_list = numpy.random.rand(num_bodies) * parameters.ymax

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

        if self.edge_type:
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
        Combines planets where necessary
        :param dists: ndarray - numpy array of distances between planets
        :return: ndarray, ndarray - masses array, to_delete index array
        """
        curr_masses = self.masses
        close_inds1, close_inds2 = numpy.where((dists != 0) & (dists < self.diams/2.5))

        if len(close_inds1):
            # determine indices to keep/delete
            close_inds1 = close_inds1[len(close_inds1) / 2:]
            close_inds2 = close_inds2[len(close_inds2) / 2:]
            cm1 = curr_masses[close_inds1]
            cm2 = curr_masses[close_inds2]

            to_increase = numpy.where(cm1>=cm2, close_inds1, close_inds2)
            to_del = numpy.where(cm1<cm2, close_inds1, close_inds2)
            curr_masses[to_increase] += numpy.sum(self.masses[to_del])

            # housekeeping: delete
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
        keep_area = parameters.area(self.diams[keep_planet])
        del_area = parameters.area(self.diams[del_planets])
        new_area = keep_area + numpy.sum(del_area)
        self.diams[keep_planet] = parameters.radius(new_area)

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

        # momentum equation, determine resulting velocity
        vrx = (mass_keep*vx_keep + numpy.sum(mass_del*vx_del)) / (mass_keep + numpy.sum(mass_del))
        vry = (mass_keep*vy_keep + numpy.sum(mass_del*vy_del)) / (mass_keep + numpy.sum(mass_del))

        self.x_velocities[keep_planet] = vrx
        self.y_velocities[keep_planet] = vry

    def draw(self, scr):
        """ Draws all the objects in Gravity
        :param scr: pygame.Surface - screen to draw on
        :param img: pygame.Surface - image to draw
        """

        xpositions = self.x_pos_list.astype(int)
        ypositions = self.y_pos_list.astype(int)
        sizes = self.diams
        scr.fill((0, 0, 0))

        for i in range(len(xpositions)):
            ballimg = parameters.image(sizes[i])
            ballimg = parameters.scale(ballimg, int((sizes[i])))
            bodyrect = ballimg.get_rect()
            bodyrect.center = (xpositions[i], ypositions[i])
            scr.blit(ballimg, bodyrect)

        planet_count = len(xpositions)
        txt = "Planets remaining: %i" % planet_count
        p_text = parameters.p_count_font.render(txt, 1, parameters.white)
        p_pos = p_text.get_rect()
        p_pos.bottomright = (parameters.xmax - 10, parameters.ymax - 10)
        scr.blit(p_text, p_pos)

    def destroy(self, ind):
        """
        Removes a planet 'object' from the arrays
        :param ind: the index to delete
        """
        self.diams = numpy.delete(self.diams, ind)
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
        self.diams = numpy.append(self.diams, 25)
        self.masses = numpy.append(self.masses, mass)
        self.x_pos_list = numpy.append(self.x_pos_list, x)
        self.y_pos_list = numpy.append(self.y_pos_list, y)
        self.x_velocities = numpy.append(self.x_velocities, 0)
        self.y_velocities = numpy.append(self.y_velocities, 0)