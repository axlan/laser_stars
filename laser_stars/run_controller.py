#! /usr/bin/env python3

import sys
import json
import threading

from laser_stars.laser_instructions import read_instr
from laser_stars.controllers.mark1 import Mark1Controller
from laser_stars.controllers.mark2 import Mark2Controller
from laser_stars.drivers.simulator import SimulatorDriver
from laser_stars.drivers.arduino_roll_pitch import ArduinoRollPitchDriver
from laser_stars.analysis.tracker import TrackerAnalysis
from laser_stars.analysis.long_exposure import LongExposureAnalysis
from laser_stars.analysis.localization import LocalizationAnalysis
from laser_stars.opencv_loop import OpenCVLoop

DRIVERS = {'arduino_roll_pitch': ArduinoRollPitchDriver,
           'simulator': SimulatorDriver}

CONTROLLERS = {'mark1': Mark1Controller,
               'mark2': Mark2Controller,}

ANALYSIS = {'tracker': TrackerAnalysis,
            'long_exposure': LongExposureAnalysis,
            'localization': LocalizationAnalysis}

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
    camera_args: kwargs to feed in a camera or video file
    analysis: List of dicts with:
        name: recorder to save video of run {list(ANALYSIS.keys())}
        args: kwargs to pass to this analysis
''')
    exit()

with open(sys.argv[1]) as fd:
    config = json.load(fd)

with open(sys.argv[2]) as fd:
    instrs = [ read_instr(line) for line in fd.readlines() ]

camera_args = config.get('camera_args', {})
with OpenCVLoop(**camera_args) as cv_loop:
    with DRIVERS[config['driver']](cv_loop, **config['driver_args']) as driver:
        if config['driver'] == 'simulator':
            cv_loop.simulator = driver
        ctrl = CONTROLLERS[config['controller']](driver, cv_loop, **config['controller_args'])
        if 'analysis' in config:
            for analysis_conf in config['analysis']:
                ANALYSIS[analysis_conf['name']](cv_loop, **analysis_conf['args'])
        ctrl.run(instrs)
