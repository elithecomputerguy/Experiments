#this code controls a Pan Tilt Camera using 2 servos to keep a face in the middle of the frame
#the servos a VERY jittery in my tests

from __future__ import print_function
import cv2 as cv
import argparse

import RPi.GPIO as GPIO
import time

topPIN = 17
bottomPIN = 27
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


        #-- In each face, detect eyes
        eyes = eyes_cascade.detectMultiScale(faceROI)
        for (x2,y2,w2,h2) in eyes:
            eye_center = (x + x2 + w2//2, y + y2 + h2//2)
            radius = int(round((w2 + h2)*0.25))
            frame = cv.circle(frame, eye_center, radius, (255, 0, 0 ), 4)
    cv.imshow('Capture - Face detection', frame)

parser = argparse.ArgumentParser(description='Code for Cascade Classifier tutorial.')
parser.add_argument('--face_cascade', help='Path to face cascade.', default='data/haarcascades/haarcascade_frontalface_alt.xml')
parser.add_argument('--eyes_cascade', help='Path to eyes cascade.', default='data/haarcascades/haarcascade_eye_tree_eyeglasses.xml')
parser.add_argument('--camera', help='Camera divide number.', type=int, default=0)
args = parser.parse_args()
face_cascade_name = args.face_cascade
eyes_cascade_name = args.eyes_cascade
face_cascade = cv.CascadeClassifier()
eyes_cascade = cv.CascadeClassifier()

#-- 1. Load the cascades
if not face_cascade.load(cv.samples.findFile(face_cascade_name)):
    print('--(!)Error loading face cascade')
    exit(0)
if not eyes_cascade.load(cv.samples.findFile(eyes_cascade_name)):
    print('--(!)Error loading eyes cascade')
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
