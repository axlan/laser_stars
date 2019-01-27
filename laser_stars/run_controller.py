#! /usr/bin/env python3

from laser_stars.laser_instructions import read_instr
from laser_stars.controllers.mark1 import Mark1Controller
from laser_stars.drivers.simulator import SimulatorDriver
from laser_stars.drivers.arduino_roll_pitch import ArduinoRollPitchDriver

#file_name = 'out/line_draw.mvs'
file_name = 'out/test.mvs'
port = "COM6"
#port = None


with open(file_name) as fd:
    instrs = [ read_instr(line) for line in fd.readlines() ]

#with SimulatorDriver(512, 512) as driver:
with ArduinoRollPitchDriver(45, 20, 5, 5, port) as driver:
    ctrl = Mark1Controller(driver, .001)
    ctrl.run(instrs)
