from typing import List, Dict, Optional, cast
import argparse
import sys

import pyzbar.pyzbar as pyzbar
import numpy as np
import cv2

from laser_stars.utils import FPSCheck

class LocalizationAnalysis(object):

    def __init__(self, cv_loop, side_len, outfile='out/tracker.avi', show=False):
        self.side_len = side_len
        self.outfile = outfile
        self.show = show
        FPS = 10
        self.update_check = FPSCheck(FPS)
        self.cv_loop = cv_loop
        self.transform = None
        if outfile:
            self.out = cv2.VideoWriter(self.outfile ,cv2.VideoWriter_fourcc(*'XVID'), FPS, (cv_loop.cam_width,cv_loop.cam_height))

        cv_loop.processing_list.append(self.cv_func)

    def order_points(pts):
        # initialzie a list of coordinates that will be ordered
        # such that the first entry in the list is the top-left,
        # the second entry is the top-right, the third is the
        # bottom-right, and the fourth is the bottom-left
        rect = np.zeros((4, 2), dtype = "float32")
    
        # the top-left point will have the smallest sum, whereas
        # the bottom-right point will have the largest sum
        s = pts.sum(axis = 1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
    
        # now, compute the difference between the points, the
        # top-right point will have the smallest difference,
        # whereas the bottom-left will have the largest difference
        diff = np.diff(pts, axis = 1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
    
        # return the ordered coordinates
        return rect

    def get_transform(frame):
        decodedObjects: List[pyzbar.Decoded] = pyzbar.decode(frame)
        if len(decodedObjects) != 4:
            return

        pts = np.array([(pt.x, pt.y) for pt in poly for poly in decodedObjects])
        
        src = order_points(pts)

        dst = np.array([(0, 0),
                        (self.side_len, 0),
                        (self.side_len, self.side_len),
                        (0, self.side_len),], np.float32)

        # compute the perspective transform matrix
        self.transform = cv2.getPerspectiveTransform(pts, dst)
        warped = cv2.warpPerspective(im, M, (self.side_len, self.side_len))

    def cv_func(self, frame, is_done):
        if is_done:
            self.out.release()
            return
        if self.update_check.check():
            if self.transform is None:
                get_transform(frame)
                return
            warped = cv2.warpPerspective(frame, self.transform, (self.side_len, self.side_len))
            self.out.write(warped)
            if self.show:
                cv2.imshow('Warped', warped)
