import sys
import argparse
import cv2
import numpy

from laser_stars.utils import FPSCheck

class LongExposureAnalysis(object):

    def __init__(self, cv_loop, outfile):
        
        self.outfile = outfile
        self.cv_loop = cv_loop
        # initialize the Red, Green, and Blue channel averages, along with
        # the total number of frames read from the file
        (self.rAvg, self.gAvg, self.bAvg) = (None, None, None)
        self.total = 0
        cv_loop.processing_list.append(self.cv_func)

    def cv_func(self, frame, is_done):
        if is_done:
            avg = cv2.merge([self.bAvg, self.gAvg, self.rAvg]).astype("uint8")
            cv2.imwrite(self.outfile, avg)
            return
        # otherwise, split the frmae into its respective channels
        (B, G, R) = cv2.split(frame.astype("float"))
        # if the frame averages are None, initialize them
        if self.rAvg is None:
            self.rAvg = R
            self.bAvg = B
            self.gAvg = G
    
        # otherwise, compute the weighted average between the history of
        # frames and the current frames
        else:
            self.rAvg = ((self.total * self.rAvg) + (1 * R)) / (self.total + 1.0)
            self.gAvg = ((self.total * self.gAvg) + (1 * G)) / (self.total + 1.0)
            self.bAvg = ((self.total * self.bAvg) + (1 * B)) / (self.total + 1.0)
    
        # increment the total number of frames read thus far
        self.total += 1
