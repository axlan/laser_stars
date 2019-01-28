#! /usr/bin/env python3

import sys
import json

from laser_stars.laser_instructions import read_instr
from laser_stars.controllers.mark1 import Mark1Controller
from laser_stars.drivers.simulator import SimulatorDriver
from laser_stars.drivers.arduino_roll_pitch import ArduinoRollPitchDriver

DRIVERS = {'arduino_roll_pitch': ArduinoRollPitchDriver,
           'simulator': SimulatorDriver}

CONTROLLERS = {'mark1': Mark1Controller}

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} CONFIG_JSON_FILE MOVEMENT_FILE')
    print(
f'''CONFIG_JSON Keys:
    driver: driver to translate desired position to output {list(DRIVERS.keys())}
    driver_args: kwargs to pass to driver
    controller: driver to translate desired position to output {list(CONTROLLERS.keys())}
    controller_args: kwargs to pass to driver
''')
    exit()

with open(sys.argv[1]) as fd:
    config = json.load(fd)

with open(sys.argv[2]) as fd:
    instrs = [ read_instr(line) for line in fd.readlines() ]

with DRIVERS[config['driver']](**config['driver_args']) as driver:
    ctrl = CONTROLLERS[config['controller']](driver, **config['controller_args'])
    ctrl.run(instrs)
