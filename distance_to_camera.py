from collections import deque
from imutils import paths
import numpy as np
import argparse
import imutils
import cv2
import time
from threading import Thread

# ***VIDEO CAM LIVE STREAM CLASS ---------------------------------------------------
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	# Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

#-----------------------------------------------------------------------------------




# ***COLOR CONSTANTS----------------------------------------------------------------
# [If new object] change these based on what object you use
colorUpper = (64, 255, 255)
colorLower = (29, 86, 6)

#-----------------------------------------------------------------------------------




# ***GET COORDINATES OF BALL FUNC---------------------------------------------------
# function that applies numerous transformations to the image and returns coordinates 
# of the largest, __ colored circle found in the frame.

def get_coordinates(image):
    blurred = cv2.GaussianBlur(image, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, colorLower, colorUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    if len(cnts) > 0:
        return max(cnts, key=cv2.contourArea)
    else: 
        return None

# ---------------------------------------------------------------------------------




# ***DISTANCE FUNC-----------------------------------------------------------------
def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / perWidth

# ---------------------------------------------------------------------------------




# ***CALIBRATION-------------------------------------------------------------------
# make more accurate in future

# [If new object] change these based on what object you use (image path, known D, known W)

# initialize the known distance from the camera to the object
KNOWN_DISTANCE = 12.0

# initialize the known object width (ball)
KNOWN_WIDTH = 4.0

# calibrating the focal length based on this picture of a ball that is 12 inches away; 4 inch diameter
image = cv2.imread("green-ball-12in.png")
calibration_c = get_coordinates(image)
((x_c,y_c), radius_calibration)  = cv2.minEnclosingCircle(calibration_c)
focalLength = ((radius_calibration * 2)  * KNOWN_DISTANCE) / KNOWN_WIDTH

# ---------------------------------------------------------------------------------




# ***BEGIN LIVE VIDEO STREAM-------------------------------------------------------- 
videostream = VideoStream(framerate=30).start()
time.sleep(1)

while True:

	# Grab frame from video stream
    frame = videostream.read()
    
    # i dont think this if-test works; basically need to test the return condition of get_coordinates if its empty
    if get_coordinates(frame).all() != None:
        c = get_coordinates(frame)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 1:
	        cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
	        cv2.circle(frame, center, 5, (0,255,255),-1)
    
        inches = distance_to_camera(KNOWN_WIDTH, focalLength, (radius*2))
        cv2.putText(frame, "%.2fft" % (inches / 12),
		(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
		2.0, (0, 255, 0), 3)

	# All of the stuff has been calculated/drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

	# Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break


# Clean up
cv2.destroyAllWindows()
videostream.stop()

# ---------------------------------------------------------------------------------