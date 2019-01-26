import numpy as np
import cv2


class SimulatorDriver():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Create a black image
        self.img = np.zeros((width, height, 3), np.uint8)
        self.cur_x = 0
        self.cur_y = 0
        self.is_on = False

    def move_to(self, x, y):
        x_pos = int(x * self.width)
        y_pos = int(y * self.width)
        if self.is_on:
            # Draw a diagonal blue line with thickness of 5 px
            cv2.line(self.img,(self.cur_x,self.cur_y),(x_pos,y_pos),(255,0,0),5)
            cv2.imshow('image',self.img)
            cv2.waitKey(1)
        self.cur_x = x_pos
        self.cur_y = y_pos

    def set_power(self, is_on):
        self.is_on = is_on

    def __enter__(self):
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.imshow('image',self.img)
        return self    

    def __exit__(self, exc_type, exc_val, exc_tb):
        cv2.waitKey(0)
        cv2.destroyAllWindows()
