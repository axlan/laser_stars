#! /usr/bin/env python3
"""constelation_mapper.py: App for creating a display pattern for the laser"""

from laser_stars.controllers.utils import dist
from laser_stars.laser_instructions import MoveTo, SetPower

import pygame

width=800
height=800
vel = .3


pygame.init()
screen = pygame.display.set_mode((width, height))
color = (0, 0, 0)

screen.fill((255, 255, 255))
pygame.display.set_caption('Constelation Mapper')
pygame.display.flip()

is_down = False
end = (0,0)
instrs = []

while True:

    event = pygame.event.wait()

    if event.type == pygame.QUIT:
        break
    if event.type != pygame.MOUSEBUTTONDOWN:
        continue

    x, y = pygame.mouse.get_pos()
    x_val = x / float(width)
    y_val = y / float(height)
    if not is_down:
        if dist(end[0] - x, end[1] - y) < 10:
            start = end
        else:
            start = (x, y)
            instrs.append(SetPower(False))
            instrs.append(MoveTo(x_val, y_val, vel))
            instrs.append(SetPower(True))
    else:
        end = (x, y)
        pygame.draw.line(screen, color, start, end, 5)
        instrs.append(MoveTo(x_val, y_val, vel))

    is_down = not is_down

    pygame.display.flip()
instrs.append(SetPower(False))

with open('out/line_draw.mvs', 'w') as fd:
    for instr in instrs:
        instr.write(fd)
