"""mark1.py: Most basic laser driver"""

from datetime import datetime
import time
import math
import json

import numpy as np

from laser_stars.laser_instructions import MoveTo, SetPower, Wait
from laser_stars.utils import dist
from laser_stars.analysis.localization import LocalizationAnalysis
from laser_stars.analysis.tracker import TrackerAnalysis

class CalibrateController():
    def __init__(self, driver, cv_loop, update_rate, tracker_conf={}, localization_conf={}, localize=False, calibration=None):
        self.driver = driver
        self.update_rate = update_rate
        self.cur_x = None
        self.cur_y = None
        self.tracker_conf = tracker_conf
        self.localization_conf = localization_conf
        self.localize = localize
        self.cv_loop = cv_loop
        self.calibration = calibration

    @staticmethod
    def line_args(pt1, pt2):
        num = pt2[1] - pt1[1]
        den = pt2[0] - pt1[0]
        m = num / den
        c = pt2[1] - m * pt2[0]
        return m, c

    @staticmethod
    def intercept(m1, c1, m2, c2):
        m = m2 - m1
        c = c1 - c2
        x = c / m
        y = m1 * x + c1
        return x, y

    @staticmethod
    def angle(pt1, pt2):
        a = -math.atan2((pt2[1] - pt1[1]), (pt2[0] - pt1[0]))
        if a < 0:
            a += 2.0 * math.pi
        return a

    @staticmethod
    def diff_angles(a1, a2):
        return math.pi - abs(abs(a1 - a2) - math.pi)

    @staticmethod
    def avr_angles(a1, a2):
        if a2 > a1:
            a2 -= 2 * math.pi
        return (a1 + a2 + math.pi / 2) / 2.0; 

    def run(self, instrs):
        CAL_SCALE = .4
        VALS = [-CAL_SCALE, CAL_SCALE]
        SAMPLES = 3
        MOVE_TIME = .2
        SAMPLE_WAIT = .2
        if self.calibration is None:
            if self.localize:
                localizer = LocalizationAnalysis(self.cv_loop, **localization_conf)
                while localizer.transform is None:
                    time.sleep(1)
                self.tracker_conf['transform'] = localizer.transform
                self.tracker_conf['side_len'] = localization_conf['side_len']
            tracker = TrackerAnalysis(self.cv_loop, **self.tracker_conf)
            

            def draw_line(x_not_y):
                measurements = []
                self.driver.move_to(0, 0)
                self.driver.set_power(True)
                for val in VALS:
                    if x_not_y:
                        self.driver.move_to(val, 0)
                    else:
                        self.driver.move_to(0, val)
                    time.sleep(MOVE_TIME)
                    tracker.previous_position = None
                    point_measurements = []
                    for i in range(SAMPLES):
                        time.sleep(SAMPLE_WAIT)
                        pos = tracker.previous_position
                        if pos is not None:
                            point_measurements.append(pos)
                        tracker.previous_position = None
                    measurements.append(np.mean(np.array(point_measurements), 0))
                return measurements[0], measurements[1]
            pt11, pt12 = draw_line(True)
            m1, c1 = self.line_args(pt11, pt12)
            pt21, pt22 = draw_line(False)
            m2, c2 = self.line_args(pt21, pt22)
            # print(pt11, pt12, m1, c1)
            # print(pt21, pt22, m2, c2)
            intercept = self.intercept(m1, c1, m2, c2)
            #print(intercept)
            intercept = intercept / np.array([tracker.cam_width, tracker.cam_height])
            #print(intercept)
            a1 = self.angle(pt11, pt12)
            a2 = self.angle(pt21, pt22)
            diff_angle = self.diff_angles(a1, a2)
            # print(math.degrees(a1))
            # print(math.degrees(a2))
            # print(math.degrees(diff_angle))
            avr_angle = self.avr_angles(a1, a2)
            #print(math.degrees(avr_angle))
            scale_x = np.linalg.norm(pt11 - pt12) / tracker.cam_width / (CAL_SCALE * 2)
            scale_y = np.linalg.norm(pt21 - pt22) / tracker.cam_height / (CAL_SCALE * 2)
            #print(scale_x, scale_y)


            self.calibration = {
                'offset': list(intercept),
                'scale': [scale_x, scale_y],
                'rotation': math.degrees(avr_angle)
            }
            print('"calibration": {}'.format(json.dumps(self.calibration)))



        angle = math.radians(self.calibration['rotation'])
        rotation = np.array([(math.cos(angle), -math.sin(angle)),
                              (math.sin(angle), math.cos(angle))])
        offset = np.array(self.calibration['offset'])
        scale = np.array(self.calibration['scale'])

        for instr in instrs:
            if type(instr) == MoveTo:
                pos = instr.pos
                pos /= scale
                pos = np.matmul(pos, rotation)
                pos -= offset
                instr.pos = pos

                if self.cur_x is None:
                    self.driver.move_to(instr.x, instr.y)
                else:
                    start_time = datetime.now()
                    start_x = self.cur_x
                    start_y = self.cur_y
                    x_dist = instr.x - start_x
                    y_dist = instr.y - start_y
                    total_dist = dist(x_dist, y_dist)
                    duration = max(total_dist / instr.vel, 0.01)
                    percent = 0
                    while percent < 1:
                        percent = (datetime.now() - start_time).total_seconds() / duration
                        percent = min(percent, 1)
                        x = start_x + x_dist * percent
                        y = start_y + y_dist * percent
                        self.driver.move_to(x, y)
                        time.sleep(self.update_rate)
                self.cur_x = instr.x
                self.cur_y = instr.y
            elif type(instr) == SetPower:
                self.driver.set_power(instr.is_on)
            elif type(instr) == Wait:
                time.sleep(instr.duration)
