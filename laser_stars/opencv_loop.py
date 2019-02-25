import cv2
import sys
import threading

class OpenCVLoop(object):

    def __init__(self, video_file=None, device_num=None, cam_width=640, cam_height=480):
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
        self.simulator = None
        self.running = True
        self.video_file = video_file
        self.cam_width = cam_width
        self.cam_height = cam_height
        self.processing_list = []
        self.device_num = device_num
        self.record_thread = threading.Thread(target=self.run)

        self.capture = None  # camera capture device

    def setup_camera_capture(self):
        """Perform camera setup for the device number (default device = 0).
        Returns a reference to the camera Capture object.
        """
        self.capture = None
        if self.video_file:
            self.capture = cv2.VideoCapture(self.video_file)
            # Check if camera opened successfully
            if (self.capture.isOpened()== False): 
                print("Error opening video stream or file")
                sys.exit(1)
        elif self.device_num:
            try:
                device = int(self.device_num)
                sys.stdout.write("Using Camera Device: {0}\n".format(device))
            except (IndexError, ValueError):
                # assume we want the 1st device
                device = 0
                sys.stderr.write("Invalid Device. Using default device 0\n")

            # Try to start capturing frames
            self.capture = cv2.VideoCapture(device)
            if not self.capture.isOpened():
                sys.stderr.write("Failed to Open Capture device. Quitting.\n")
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

    def run(self):
        if self.video_file is not None or self.device_num is not None:
            # Set up the camera capture
            self.setup_camera_capture()

        while self.running:
            # 1. capture the current image
            if self.capture is not None:
                success, frame = self.capture.read()
                if not success:  # no image captured... end the processing
                    sys.stderr.write("Could not read camera frame. Quitting\n")
                    sys.exit(1)
            elif self.simulator:
                frame = self.simulator.img.copy()
            else:
                frame = None
            for func in self.processing_list:
                func(frame, False)
            cv2.waitKey(10)
        for func in self.processing_list:
                func(frame, True)
        cv2.waitKey(10)

    def __enter__(self):
        self.record_thread.start()
        return self    

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.running = False
        self.record_thread.join()
