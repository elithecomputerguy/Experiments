from __future__ import print_function
import cv2 as cv
import argparse

import RPi.GPIO as GPIO
import time

topPIN = 13
bottomPIN = 19
GPIO.setmode(GPIO.BCM)
GPIO.setup(topPIN, GPIO.OUT)
GPIO.setup(bottomPIN, GPIO.OUT)

top = GPIO.PWM(topPIN, 50) # GPIO 17 for PWM with 50Hz
top.start(2.5) # Initialization
bottom = GPIO.PWM(bottomPIN, 50) # GPIO 17 for PWM with 50Hz
bottom.start(2.5) # Initialization

min_top = .1
max_top = 8

min_bottom = .1
max_bottom = 10.5

bottom_position = 5
top_position = 4

bottom.ChangeDutyCycle(bottom_position)
top.ChangeDutyCycle(top_position)

def detectAndDisplay(frame):
    global bottom_position
    global top_position

    frame_gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame_gray = cv.equalizeHist(frame_gray)
    #-- Detect faces
    faces = face_cascade.detectMultiScale(frame_gray, minSize=(100,100))
    for (x,y,w,h) in faces:
        center = (x + w//2, y + h//2)
        frame = cv.ellipse(frame, center, (w//2, h//2), 0, 0, 360, (255, 0, 255), 4)
        faceROI = frame_gray[y:y+h,x:x+w]

        font = cv.FONT_HERSHEY_SIMPLEX
        cv.putText(frame, str(center), (50, 50), font, 1, (0, 255, 255), 2, cv.LINE_4)

        if center[0] < 400 and bottom_position >= .5:
            bottom_position = bottom_position - .2
            bottom.ChangeDutyCycle(bottom_position)
            time.sleep(.1)

        if center[0] > 250 and bottom_position <= 10:
            bottom_position = bottom_position + .2
            bottom.ChangeDutyCycle(bottom_position)
            time.sleep(.1)

        if center[1] < 150 and top_position >= .5:
            top_position = top_position + .2
            top.ChangeDutyCycle(top_position)
            time.sleep(.1)

        if center[1] > 300 and top_position <= 10:
            top_position = top_position - .2
            top.ChangeDutyCycle(top_position)
            time.sleep(.1)    

    cv.imshow('Capture - Face detection', frame)

parser = argparse.ArgumentParser(description='Code for Cascade Classifier tutorial.')
parser.add_argument('--face_cascade', help='Path to face cascade.', default='data/louis-cascade/cascade.xml')
parser.add_argument('--camera', help='Camera divide number.', type=int, default=0)
args = parser.parse_args()
face_cascade_name = args.face_cascade
face_cascade = cv.CascadeClassifier()

#-- 1. Load the cascades
if not face_cascade.load(cv.samples.findFile(face_cascade_name)):
    print('--(!)Error loading face cascade')
    exit(0)
camera_device = args.camera
#-- 2. Read the video stream
cap = cv.VideoCapture(camera_device)
if not cap.isOpened:
    print('--(!)Error opening video capture')
    exit(0)
while True:
    ret, frame = cap.read()
    if frame is None:
        print('--(!) No captured frame -- Break!')
        break

    detectAndDisplay(frame)

    if cv.waitKey(10) == 27:
        break