#! /usr/bin/env python3

from laser_stars.laser_instructions import read_instr
from laser_stars.controllers.mark1 import Mark1Controller
from laser_stars.drivers.simulator import SimulatorDriver


with open('out/line_draw.mvs') as fd:
    instrs = [ read_instr(line) for line in fd.readlines() ]

with SimulatorDriver(512, 512) as driver:
    ctrl = Mark1Controller(driver, .001)
    ctrl.run(instrs)
