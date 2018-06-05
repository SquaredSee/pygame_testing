#!/usr/bin/env python3

import sys
import pygame
from pygame.locals import *

X = 0
Y = 1
F_INCREMENT = 100


class State(object):
    """ Game state variables """
    __slots__ = ('s_width', 's_height', 'running', 't', 'dt', 'fps')


class Derivative(object):
    def __init__(self, dt=None, obj=None, der=None):
        if not dt:
            dt = state.dt
        if obj:
            _temp_obj = obj
            _temp_obj.rect.x = obj.rect.x + der.dx * state.dt
            _temp_obj.rect.y = obj.rect.y + der.dy * state.dt
            _temp_obj.x_vel = obj.x_vel + der.dvx * state.dt
            _temp_obj.y_vel = obj.y_vel + der.dvy * state.dt

            self.dx = _temp_obj.x_vel
            self.dy = _temp_obj.y_vel
            self.dvx = acceleration(_temp_obj, state.t + dt, 'x')
            self.dvy = acceleration(_temp_obj, state.t + dt, 'y')
        else:
            self.dx = 0
            self.dy = 0
            self.dvx = 0
            self.dvy = 0


class Entity(object):
    def __init__(self, width, height):
        self.surface = pygame.Surface((width, height)).convert()
        self.surface.fill((255, 255, 255))
        self.rect = self.surface.get_rect()
        self.pos = [self.rect.x, self.rect.y]  # required because self.rect rounds to the nearest int
        self.mass = 1.  # Assume unit mass
        self.x_vel = 0.
        self.y_vel = 0.
        self.x_acc = 0.
        self.y_acc = 0.
        self.x_force = 0.
        self.y_force = 0.

    def update(self):
        a = Derivative(obj=self, der=Derivative())
        b = Derivative(obj=self, dt=(state.dt * .5), der=a)
        c = Derivative(obj=self, dt=(state.dt * .5), der=b)
        d = Derivative(obj=self, der=c)

        dxdt = 1. / 6. * (a.dx + 2. * (b.dx + c.dx) + d.dx)
        dydt = 1. / 6. * (a.dy + 2. * (b.dy + c.dy) + d.dy)
        dvxdt = 1. / 6. * (a.dvx + 2. * (b.dvx + c.dvx) + d.dvx)
        dvydt = 1. / 6. * (a.dvy + 2. * (b.dvy + c.dvy) + d.dvy)

        self.pos[X] = (self.pos[X] + (dxdt * state.dt))
        self.pos[Y] = (self.pos[Y] + (dydt * state.dt))

        if self.pos[Y] < 0:
            self.pos[Y] = 0.
            self.y_vel = 0.  # make the box bounce
        elif self.pos[Y] > state.s_height:
            self.pos[Y] = state.s_height
            self.y_vel = 0.

        if self.pos[X] < 0:
            self.pos[X] = 0
            self.x_vel = 0  # make the box bounce
        elif self.pos[X] > state.s_width:
            self.pos[X] = state.s_width
            self.x_vel = 0

        self.rect.y = convert_y(self.pos[Y] + 10)
        self.rect.x = self.pos[X]
        self.x_vel = self.x_vel + dvxdt * state.dt
        self.y_vel = self.y_vel + dvydt * state.dt


def acceleration(obj, t, direction):
    """ Uses a=F/m to calculate acceleration """
    if direction == 'x':
        new_acc = obj.x_force / float(obj.mass)
    elif direction == 'y':
        g = obj.mass * 9.81 * 5
        net_y_force = obj.y_force - g
        new_acc = net_y_force / float(obj.mass)
    #print('acc ' + direction + ': ' + str(new_acc))
    return new_acc


def convert_y(y):
    """ converts y so bottom left is (0,0) instead of top left """
    return state.s_height - y


def main():
    global state
    state = State()
    state.s_width = 600  # screen width
    state.s_height = 600  # screen height
    state.running = True  # main loop boolean
    state.fps = 60.  # Target FPS
    state.t = 0.  # runtime
    state.dt = 1. / state.fps

    pygame.init()

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((state.s_width, state.s_height))
    pygame.display.set_caption('Pygame Physics Simulation')

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))

    box = Entity(10, 10)
    box.topleft = (0, 0)
    #box.midbottom = ((background.get_width() / 2.), 0)

    while state.running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    box.x_force += F_INCREMENT
                elif event.key == pygame.K_LEFT:
                    box.x_force -= F_INCREMENT
                elif event.key == pygame.K_UP:
                    box.y_force += F_INCREMENT
                elif event.key == pygame.K_DOWN:
                    box.y_force -= F_INCREMENT

                # make sure force doesn't go crazy
                if box.x_force > F_INCREMENT:
                    box.x_force = F_INCREMENT
                if box.y_force > F_INCREMENT:
                    box.y_force = F_INCREMENT

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    box.x_force -= F_INCREMENT
                elif event.key == pygame.K_LEFT:
                    box.x_force += F_INCREMENT
                elif event.key == pygame.K_UP:
                    box.y_force -= F_INCREMENT
                elif event.key == pygame.K_DOWN:
                    box.y_force += F_INCREMENT

                # make sure force doesn't go crazy
                if box.x_force < -F_INCREMENT:
                    box.x_force = -F_INCREMENT
                if box.y_force < -F_INCREMENT:
                    box.y_force = -F_INCREMENT

        box.update()  # updates the state of the box

        # Render changes
        screen.blit(background, (0, 0))
        screen.blit(box.surface, box.rect)
        pygame.display.flip()

        print('box.rect.x @ {0:.3f}: {1:.3f}'.format(state.t, box.rect.x))
        print('box.x_vel @ {0:.3f}: {1:.3f}'.format(state.t, box.x_vel))
        print('state.rect.y @ {0:.3f}: {1:.3f}'.format(state.t, box.rect.y))
        print('state.y_vel @ {0:.3f}: {1:.3f}\n'.format(state.t, box.y_vel))

        clock.tick(state.fps)
        state.t += state.dt


if __name__ == '__main__':
    main()
