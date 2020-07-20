# import the necessary packages
# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

from imutils import paths
import numpy as np
import imutils
import cv2
import time
from threading import Thread


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

def find_marker(image):
	# convert the image to grayscale, blur it, and detect edges
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	gray = cv2.GaussianBlur(gray, (5, 5), 0)
	edged = cv2.Canny(gray, 35, 125)
	# find the contours in the edged image and keep the largest one;
	# we'll assume that this is our piece of paper in the image
	cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)

    # ***current set up just sees which contours on the screen has the biggest
    # ***area, but we need to use something like color or another property
    # ***to accuratly detect the basketball.
    
	c = max(cnts, key = cv2.contourArea)
	# compute the bounding box of the of the paper region and return it
	return cv2.minAreaRect(c)

def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / perWidth


# # ***this is for calibration/ we need to change this 
# # ***to make the calibration process better

# # initialize the known distance from the camera to the object, which
# # in this case is 24 inches
# KNOWN_DISTANCE = 24.0

# # initialize the known object width, which in this case, the piece of
# # paper is 12 inches wide
# KNOWN_WIDTH = 11.0

# # load the furst image that contains an object that is KNOWN TO BE 2 feet
# # from our camera, then find the paper marker in the image, and initialize
# # the focal length
# image = cv2.imread("images/2ft.png")
# marker = find_marker(image)
# focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH


# # ***the actual distance test; works for images, so we need to change for 
# # ***live video input

# # loop over the images
# for imagePath in sorted(paths.list_images("images")):
# 	# load the image, find the marker in the image, then compute the
# 	# distance to the marker from the camera
# 	image = cv2.imread(imagePath)
# 	marker = find_marker(image)
# 	inches = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])
# 	# draw a bounding box around the image and display it
# 	box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
# 	box = np.int0(box)
# 	cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
# 	cv2.putText(image, "%.2fft" % (inches / 12),
# 		(image.shape[1] - 200, image.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
# 		2.0, (0, 255, 0), 3)
# 	cv2.imshow("image", image)
# 	cv2.waitKey(0)

orangeLower = (112, 65, 19)
orangeUpper = (255, 255, 88)

videostream = VideoStream(framerate=30).start()
time.sleep(1)

while True:

	# Grab frame from video stream
    frame = videostream.read()

    blurred = cv2.GaussianBlur(frame, (11,11), 0)
    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, orangeLower, orangeUpper)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    center = None
    
    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        ((x,y), radius) = cv2.minEnclosingCircle(c)
        M = cv2.moments(c)
        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

        if radius > 10:

	        cv2.circle(frame, (int(x), int(y)), int(radius), (0,255,255), 2)
	        cv2.circle(frame, center, 5, (0,255,255),-1)




	# All the results have been drawn on the frame, so it's time to display it.
    cv2.imshow('Object detector', frame)

	# Press 'q' to quit
    if cv2.waitKey(1) == ord('q'):
        break


# Clean up
cv2.destroyAllWindows()
videostream.stop()
