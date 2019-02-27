"""mark1.py: Most basic laser driver"""

from datetime import datetime
import time
import math

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
    def angle(m):
        a = math.atan(m)
        if a < 0:
            a += 2.0 * math.pi
        return math.atan(m)

    def run(self, instrs):
        VALS = [-.4, .4]
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
            print(pt11, pt12, m1, c1)
            print(pt21, pt22, m2, c2)
            intercept = self.intercept(m1, c1, m2, c2)
            print(intercept)
            a1 = math.degrees(math.atan2((pt12[1] - pt11[1]), (pt12[0] - pt11[0])))
            a2 = math.degrees(math.atan2((pt22[1] - pt21[1]), (pt22[0] - pt21[0])))
            print(a1)
            print(a2)
            

            self.driver.move_to(0, 0)
            self.driver.move_to(0, 0)
            self.driver.move_to(0, 0)
            self.driver.move_to(0, 0)
            self.driver.move_to(0, 0)
            
        for instr in instrs:
            if type(instr) == MoveTo:
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
