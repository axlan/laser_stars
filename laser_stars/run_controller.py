#! /usr/bin/env python3

import sys
import json
import threading

from laser_stars.laser_instructions import read_instr
from laser_stars.controllers.mark1 import Mark1Controller
from laser_stars.drivers.simulator import SimulatorDriver
from laser_stars.drivers.arduino_roll_pitch import ArduinoRollPitchDriver
#from laser_stars.recorders.tracker import TrackerRecorder
from laser_stars.recorders.simulator import SimulatorRecorder

DRIVERS = {'arduino_roll_pitch': ArduinoRollPitchDriver,
           'simulator': SimulatorDriver}

CONTROLLERS = {'mark1': Mark1Controller}

RECORDER = {'simulator': SimulatorRecorder,
            'tracker': Mark1Controller}

if len(sys.argv) != 3:
    print(f'Usage: {sys.argv[0]} CONFIG_JSON_FILE MOVEMENT_FILE')
    print(
f'''CONFIG_JSON 
REQUIRED KEYS
    driver: driver to translate desired position to output {list(DRIVERS.keys())}
    driver_args: kwargs to pass to driver
    controller: driver to translate desired position to output {list(CONTROLLERS.keys())}
    controller_args: kwargs to pass to driver
OPTIONAL KEYS
    recorder: recorder to save video of run {list(RECORDER.keys())}
    recorder_args: kwargs to pass to recorder
''')
    exit()

with open(sys.argv[1]) as fd:
    config = json.load(fd)

with open(sys.argv[2]) as fd:
    instrs = [ read_instr(line) for line in fd.readlines() ]

with DRIVERS[config['driver']](**config['driver_args']) as driver:
    if 'recorder' in config:
        recorder = RECORDER[config['recorder']](driver, **config['recorder_args'])
        record_thread = threading.Thread(target=recorder.run)
        record_thread.start()
    ctrl = CONTROLLERS[config['controller']](driver, **config['controller_args'])
    ctrl.run(instrs)
