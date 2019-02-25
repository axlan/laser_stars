from math import cos, sin, radians
from random import random

import numpy as np
import cv2

from laser_stars.utils import FPSCheck

class SimulatorDriver():
    _WIN_NAME = "sim_image"
    def __init__(self, cv_loop, width, height, trail=True, scale=[1,1], orientation=0.0, noise=0, fps=10, outfile=None):
        self.trail = trail
        self.running = True
        self.width = width
        self.noise = noise
        self.height = height
        # Create a black image
        self.img = np.zeros((width, height, 3), np.uint8)
        self.cur_x = 0
        self.cur_y = 0
        self.is_on = False
        self.outfile = outfile
        self.scale = np.array(scale) * np.array([self.width, self.height])
        orientation = radians(orientation)
        self.rotation = np.array([(cos(orientation), -sin(orientation)),
                                  (sin(orientation), cos(orientation))])
        self.update_check = FPSCheck(fps)
        if outfile:
            # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
            self.out = cv2.VideoWriter(self.outfile ,cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))
        else:
            self.out = None
        cv_loop.processing_list.append(self.cv_func)

    def move_to(self, x, y):
        noise_x = (random() - .5) * self.noise
        noise_y = (random() - .5) * self.noise
        pos = (np.array([x + noise_x, y + noise_y])) * self.scale
        pos = np.matmul(pos, self.rotation)      
        x_pos = int(pos[0]) 
        y_pos = int(pos[1])
        if self.is_on:
            # Draw a diagonal blue line with thickness of 5 px
            if self.trail:
                cv2.line(self.img,(self.cur_x,self.cur_y),(x_pos,y_pos),(255,0,0),5)
            else:
                self.img = np.zeros((self.width, self.height, 3), np.uint8)
                cv2.circle(self.img, (self.cur_x,self.cur_y), 5, [255,0,0],-1)
        self.cur_x = x_pos
        self.cur_y = y_pos

    def set_power(self, is_on):
        self.is_on = is_on

    def __enter__(self):
        return self    

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def cv_func(self, frame, is_done):
        if is_done and self.out:
            self.out.release()
            return
        if self.update_check.check():
            cv2.imshow(self._WIN_NAME,self.img)
            if self.out:
                self.out.write(self.img)
