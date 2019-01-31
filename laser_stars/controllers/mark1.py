"""mark1.py: Most basic laser driver"""

from laser_stars.laser_instructions import MoveTo, SetPower, Wait
from laser_stars.utils import dist

from datetime import datetime
import time

class Mark1Controller():
    def __init__(self, driver, cv_loop, update_rate):
        self.driver = driver
        self.update_rate = update_rate
        self.cur_x = None
        self.cur_y = None
        self.cv_loop = cv_loop

    def run(self, instrs):
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
                    duration = total_dist / instr.vel
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
