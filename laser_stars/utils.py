
import math
from datetime import datetime

def dist(x, y):
    return math.sqrt(x**2 + y**2)

class FPSCheck():
    def __init__(self, fps):
        self.fps = fps
        self.last_update = datetime.now()

    def check(self):
        if (datetime.now() - self.last_update).total_seconds() > 1.0 / float(self.fps):
            self.last_update = datetime.now()
            return True
        return False
