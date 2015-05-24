__author__ = 'Matt'

import pygame
import parameters

class Menu(object):
    def __init__(self):
        # font objects
        title_text = parameters.title_font.render("Universe Simulator 2k15", 1, parameters.white)

        planet_count_text = parameters.menu_font.render("Amount of planets", 1, parameters.white)
        edge_text = parameters.menu_font.render("Universe type:", 1, parameters.white)
        in_vel_text = parameters.menu_font.render("Initial excitation:", 1, parameters.white)
        dif_mass_text = parameters.menu_font.render("Realtive size factor:", 1, parameters.white)
        start_text = parameters.start_font.render("BEGIN SIMULATION", 1, parameters.white)

        bounce_text = parameters.menu_font.render("Contained", 1, parameters.blue)
        wrap_text = parameters.menu_font.render("Wrapped", 1, parameters.blue)
        self.edge_options = [bounce_text, wrap_text]

        self.fonts = [title_text, planet_count_text, edge_text, in_vel_text, dif_mass_text, start_text]

        # positions
        title_pos = (parameters.xmax/2, parameters.ymax/4)

        planet_count_pos = (parameters.xmax/5, parameters.ymax/2)
        edge_pos = (2*parameters.xmax/5, parameters.ymax/2)
        in_vel_pos = (3*parameters.xmax/5, parameters.ymax/2)
        dif_mass_pos = (4*parameters.xmax/5, parameters.ymax/2)

        start_pos = (parameters.xmax/2, 13*parameters.ymax/16)

        self.poses = [title_pos, planet_count_pos, edge_pos, in_vel_pos, dif_mass_pos, start_pos]

        # shapes
        p_count_up = (planet_count_pos[0], planet_count_pos[1] - 50)
        p_count_down = (planet_count_pos[0], planet_count_pos[1] + 100)
        in_vel_pos_up = (in_vel_pos[0], in_vel_pos[1] - 50)
        in_vel_pos_down = (in_vel_pos[0], in_vel_pos[1] + 100)
        dif_mass_pos_up = (dif_mass_pos[0], dif_mass_pos[1] - 50)
        dif_mass_pos_down = (dif_mass_pos[0], dif_mass_pos[1] + 100)
        edge_option_pos = (edge_pos[0], edge_pos[1] + 50)
        edge_toggle_pos = (edge_pos[0]-10, edge_pos[1] + 35)

        self.up_arrows = [p_count_up, in_vel_pos_up, dif_mass_pos_up]
        self.down_arrows = [p_count_down, in_vel_pos_down, dif_mass_pos_down]

        self.edge_toggle = [True, edge_option_pos, edge_toggle_pos]
        self.opt_poses = [planet_count_pos, in_vel_pos, dif_mass_pos]
        self.values = [parameters.num_planets, 0.0, 1.0]

        self.limits = [[10, 250], [0, 5], [1, 5]]

    def draw(self, screen, mouse_pos, clicked):
        """
        Draws ALL THE THINGS
        :param screen: pygame.Surface to draw on
        """
        # 'refresh' screen
        screen.fill(parameters.black)

        # option text
        if self.edge_toggle[0]:
            edge_txt = self.edge_options[0]
        else:
            edge_txt = self.edge_options[1]

        # draw buttons
        startpos = parameters.startimg.get_rect()
        startpos.center = self.poses[-1]
        edge_pos = edge_txt.get_rect()
        edge_pos.center = self.edge_toggle[2]

        start = screen.blit(parameters.startimg, startpos)
        toggle = screen.blit(parameters.toggleimg, edge_pos)

        #check to toggle edge type
        if toggle.collidepoint(mouse_pos) and clicked:
            self.edge_toggle[0] = not self.edge_toggle[0]

        # draw fonts (title, options, start)
        for ind, f in enumerate(self.fonts):
            f_pos = f.get_rect()
            f_pos.center = self.poses[ind]
            screen.blit(f, f_pos)

        edge_txt_pos = edge_txt.get_rect()
        edge_txt_pos.center = self.edge_toggle[1]
        screen.blit(edge_txt, edge_txt_pos)  # lone edge-options

        # draw arrows
        for ind, u in enumerate(self.up_arrows):
            a = self.draw_arrow(screen, u, parameters.arr_base, parameters.arr_height, True)
            if a.collidepoint(mouse_pos):
                self.draw_arrow(screen, u, parameters.arr_base, parameters.arr_height, False)
                if clicked:
                    self.values[ind] = self.alter_values(ind, True)

        for ind2, d in enumerate(self.down_arrows):
            a = self.draw_arrow(screen, d, parameters.arr_base, parameters.arr_height, True, False)
            if a.collidepoint(mouse_pos):
                self.draw_arrow(screen, d, parameters.arr_base, parameters.arr_height, False, False)
                if clicked:
                    self.values[ind2] = self.alter_values(ind2, False)

        # draw initial values
        for i, opt in enumerate(self.opt_poses):
            in_val = str(self.values[i])
            in_txt = parameters.opt_font.render(in_val, 1, parameters.white)
            in_pos = in_txt.get_rect()
            in_pos.center = (opt[0], opt[1] + 50)
            screen.blit(in_txt, in_pos)

        return start.collidepoint(mouse_pos) and clicked  # returns True when clicked on BEGIN (should)

    def draw_arrow(self, screen, position, base, height, fill=True, up=True):
        """
        Draws a triangular arrow to the screen given its _geometrical_ center
        :param screen: pygame.Surface - screen to draw arrow on to
        :param position: tuple (x, y) - position of arrow
        :param fill: bool - draw (True) or outline (False) the triangle
        :param up: bool - pointing up or down, default up
        """
        x, y = position[0], position[1]
        if up:
            a = (x - base/2, y + height/3)
            b = (x + base/2, y + height/3)
            c = (x, y - 2*height/3)
        else:
            a = (x - base/2, y - height/3)
            b = (x + base/2, y - height/3)
            c = (x, y + 2 * height/3)

        if fill:
            return pygame.draw.polygon(screen, parameters.white, (a, b, c))
        else:
            return pygame.draw.lines(screen, parameters.red, 1, (a, b, c))

    def alter_values(self, ind, increase):
        if ind == 0:
            if increase:
                new_val = self.values[0] + 5
            else:
                new_val = self.values[0] - 5

        else:
            if increase:
                new_val = self.values[ind] + 0.1
            else:
                new_val = self.values[ind] - 0.1

        if new_val <= self.limits[ind][0]:
            new_val = self.limits[ind][0]

        if new_val >= self.limits[ind][1]:
            new_val = self.limits[ind][1]

        return round(new_val, 1)