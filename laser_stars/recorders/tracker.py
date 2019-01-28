import sys
import argparse
import cv2
import numpy

class TrackerRecorder(object):

    def __init__(self, driver, video_file=None, cam_width=640, cam_height=480, hue_min=20, hue_max=160,
                 sat_min=100, sat_max=255, val_min=200, val_max=256, outfile='out/tracker.avi', show=False):
        """
        * ``cam_width`` x ``cam_height`` -- This should be the size of the
        image coming from the camera. Default is 640x480.
        HSV color space Threshold values for a RED laser pointer are determined
        by:
        * ``hue_min``, ``hue_max`` -- Min/Max allowed Hue values
        * ``sat_min``, ``sat_max`` -- Min/Max allowed Saturation values
        * ``val_min``, ``val_max`` -- Min/Max allowed pixel values
        If the dot from the laser pointer doesn't fall within these values, it
        will be ignored.
        """

        self.video_file = video_file
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.hue_min = hue_min
        self.hue_max = hue_max
        self.sat_min = sat_min
        self.sat_max = sat_max
        self.val_min = val_min
        self.val_max = val_max
        self.driver = driver
        self.outfile = outfile
        self.show = show

        self.capture = None  # camera capture device
        self.channels = {
            'hue': None,
            'saturation': None,
            'value': None,
            'laser': None,
        }

        self.previous_position = None
        self.trail = numpy.zeros((self.cam_height, self.cam_width, 3),
                                 numpy.uint8)

    def setup_camera_capture(self, device_num=0):
        """Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.
        """

        if self.video_file:
            self.capture = cv2.VideoCapture(self.video_file)
            # Check if camera opened successfully
            if (self.capture.isOpened()== False): 
                print("Error opening video stream or file")
                sys.exit(1)
        else:
            try:
                device = int(device_num)
                sys.stdout.write("Using Camera Device: {0}\n".format(device))
            except (IndexError, ValueError):
                # assume we want the 1st device
                device = 0
                sys.stderr.write("Invalid Device. Using default device 0\n")

            # Try to start capturing frames
            self.capture = cv2.VideoCapture(device)
            if not self.capture.isOpened():
                sys.stderr.write("Faled to Open Capture device. Quitting.\n")
                sys.exit(1)

            # set the wanted image size from the camera
            self.capture.set(
                cv2.cv.CV_CAP_PROP_FRAME_WIDTH if cv2.__version__.startswith('2') else cv2.CAP_PROP_FRAME_WIDTH,
                self.cam_width
            )
            self.capture.set(
                cv2.cv.CV_CAP_PROP_FRAME_HEIGHT if cv2.__version__.startswith('2') else cv2.CAP_PROP_FRAME_HEIGHT,
                self.cam_height
            )
        return self.capture

    def threshold_image(self, channel):
        if channel == "hue":
            minimum = self.hue_min
            maximum = self.hue_max
        elif channel == "saturation":
            minimum = self.sat_min
            maximum = self.sat_max
        elif channel == "value":
            minimum = self.val_min
            maximum = self.val_max

        (t, tmp) = cv2.threshold(
            self.channels[channel],  # src
            maximum,  # threshold value
            0,  # we dont care because of the selected type
            cv2.THRESH_TOZERO_INV  # t type
        )

        (t, self.channels[channel]) = cv2.threshold(
            tmp,  # src
            minimum,  # threshold value
            255,  # maxvalue
            cv2.THRESH_BINARY  # type
        )

        if channel == 'hue':
            # only works for filtering red color because the range for the hue
            # is split
            self.channels['hue'] = cv2.bitwise_not(self.channels['hue'])

    def track(self, frame, mask):
        """
        Track the position of the laser pointer.
        Code taken from
        http://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
        """
        center = None

        countours = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)[-2]

        # only proceed if at least one contour was found
        if len(countours) > 0:
            # find the largest contour in the mask, then use
            # it to compute the minimum enclosing circle and
            # centroid
            c = max(countours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            moments = cv2.moments(c)
            if moments["m00"] > 0:
                center = int(moments["m10"] / moments["m00"]), \
                         int(moments["m01"] / moments["m00"])
            else:
                center = int(x), int(y)

            # only proceed if the radius meets a minimum size
            if radius > 10:
                # draw the circle and centroid on the frame,
                cv2.circle(frame, (int(x), int(y)), int(radius),
                           (0, 255, 255), 2)
                cv2.circle(frame, center, 5, (0, 0, 255), -1)
                # then update the ponter trail
                if self.previous_position:
                    cv2.line(self.trail, self.previous_position, center,
                             (255, 255, 255), 2)

        cv2.add(self.trail, frame, frame)
        self.previous_position = center

    def detect(self, frame):
        hsv_img = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # split the video frame into color channels
        h, s, v = cv2.split(hsv_img)
        self.channels['hue'] = h
        self.channels['saturation'] = s
        self.channels['value'] = v

        # Threshold ranges of HSV components; storing the results in place
        self.threshold_image("hue")
        self.threshold_image("saturation")
        self.threshold_image("value")

        # Perform an AND on HSV components to identify the laser!
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['hue'],
            self.channels['value']
        )
        self.channels['laser'] = cv2.bitwise_and(
            self.channels['saturation'],
            self.channels['laser']
        )

        self.track(frame, self.channels['laser'])

    def run(self):
        # Set up the camera capture
        self.setup_camera_capture()
        out = cv2.VideoWriter(self.outfile ,cv2.VideoWriter_fourcc(*'MJPG'), 10, (self.cam_width,self.cam_height))
        if self.show:
            cv2.namedWindow('LaserPointer')

        while self.driver.running:
            # 1. capture the current image
            success, frame = self.capture.read()
            if not success:  # no image captured... end the processing
                sys.stderr.write("Could not read camera frame. Quitting\n")
                sys.exit(1)
            self.detect(frame)
            out.write(frame)
            if self.show:
                cv2.imshow('LaserPointer', frame)
                cv2.waitKey(10)
        out.release()
