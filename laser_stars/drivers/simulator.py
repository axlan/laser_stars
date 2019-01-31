import numpy as np
import cv2
from laser_stars.utils import FPSCheck

class SimulatorDriver():
    _WIN_NAME = "sim_image"
    def __init__(self, cv_loop, width, height, fps=10, outfile=None):
        self.running = True
        self.width = width
        self.height = height
        # Create a black image
        self.img = np.zeros((width, height, 3), np.uint8)
        self.cur_x = 0
        self.cur_y = 0
        self.is_on = False
        self.outfile = outfile
        self.update_check = FPSCheck(fps)
        if outfile:
            # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
            self.out = cv2.VideoWriter(self.outfile ,cv2.VideoWriter_fourcc(*"XVID"), fps, (width, height))
        cv_loop.processing_list.append(self.cv_func)

    def move_to(self, x, y):
        x_pos = int(x * self.width)
        y_pos = int(y * self.width)
        if self.is_on:
            # Draw a diagonal blue line with thickness of 5 px
            cv2.line(self.img,(self.cur_x,self.cur_y),(x_pos,y_pos),(255,0,0),5)
        self.cur_x = x_pos
        self.cur_y = y_pos

    def set_power(self, is_on):
        self.is_on = is_on

    def __enter__(self):
        return self    

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def cv_func(self, frame, is_done):
        if is_done:
            self.out.release()
            return
        if self.update_check.check():
            cv2.imshow(self._WIN_NAME,self.img)
            self.out.write(self.img)
