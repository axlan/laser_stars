import cv2
import numpy as np
import time

class SimulatorRecorder():
    def __init__(self, driver, fps, outfile):
        self.driver = driver
        self.fps = fps
        self.outfile = outfile

    def run(self):
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        out = cv2.VideoWriter(self.outfile ,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (self.driver.width,self.driver.height))
        while self.driver.running:
            out.write(self.driver.img)
            time.sleep(1.0 / float(self.fps))
        out.release()
