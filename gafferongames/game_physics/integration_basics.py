#!/usr/bin/env python3

import sys
import pygame
from pygame.locals import *

# http://gafferongames.com/game-physics/integration-basics/

S_HEIGHT = 500
S_WIDTH = 200


def convert_y(y, height):
    return height - y


class State(object):
    """ Class containing state variables """
    __slots__ = ('y', 'v')


class Derivative(object):
    """ Class containing derivative values """
    def __init__(self, dy, dv):
        self.dy = dy
        self.dv = dv
    # dy = velocity, dv = acceleration
    # GOTTA REMEMBER THIS SHIT FROM CALCULUS I GUESS


def acceleration(state, t):
    return -9.8


def evaluate(init_state, t, dt, d):
    state = State()
    state.y = init_state.y + d.dy * dt
    state.v = init_state.v + d.dv * dt

    output = Derivative(state.v, acceleration(state, t + dt))
    return output


def integrate(state, t, dt):
    a = evaluate(state, t, dt, Derivative(0, 0))
    b = evaluate(state, t, dt * 0.5, a)
    c = evaluate(state, t, dt * 0.5, b)
    d = evaluate(state, t, dt, c)

    dydt = 1. / 6. * (a.dy + 2 * (b.dy + c.dy) + d.dy)
    dvdt = 1. / 6. * (a.dv + 2 * (b.dv + c.dv) + d.dv)

    test = State()
    test.y = state.y + dydt * dt
    test.v = state.v + dvdt * dt
    return test


def main():
    state = State()
    state.y = 0
    state.v = 50

    pygame.init()
    screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
    screen.fill((255, 255, 255))

    clock = pygame.time.Clock()

    fps = 30

    running = True
    t = 0
    dt = 1. / fps
    while running:
        clock.tick(fps)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    t = 0
                    state.y = 0
                    state.v = 15

        if t < 20:
            state = integrate(state, t, dt)
            if state.y <= 0:
                state.v = -state.v

            print('state.y @ {}: {}'.format(t, state.y))
            print('state.v @ {}: {}\n'.format(t, state.v))
            t += dt

        screen.fill((255, 255, 255))
        pygame.draw.rect(screen, (0, 0, 0),
            (95, convert_y(state.y, S_HEIGHT) - 10, 10, 10), 0)
        pygame.display.update()


if __name__ == '__main__':
    main()
