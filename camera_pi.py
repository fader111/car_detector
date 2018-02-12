#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import io
import threading
import cv2
import picamera
from picamera.array import PiRGBArray
import numpy as np

class Camera(object):
    thread = None  # background thread that reads frames from camera
    thread2 = None  # background thread that reads frames from camera
    frame = 1  # current frame is stored here by background thread
    frameCV2 = None # same, but as a numpy array
    last_access = 0  # time of last client access to the camera

    def initialize(self):
        if Camera.thread is None:
            # start background frame thread
            Camera.thread = threading.Thread(target=self._thread)
            Camera.thread.start()

            # wait until frames start to be available
            while self.frameCV2 is None:
                print('Hold!')
                time.sleep(0)

    def get_frame(self):
        Camera.last_access = time.time()
        self.initialize()
        self.frame = cv2.imencode('.jpg', self.frameCV2)[1].tobytes()              
        return self.frame

    def get_frame_for_internal_proc(self): # store frame for cv2 
        Camera.last_access = time.time()
        self.initialize()
        #self.frameCV2 = cv2.imread('dt2/1.jpg')
        return self.frameCV2

    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (800, 600)
            camera.hflip = True
            camera.vflip = True
            # let camera warm up
            time.sleep(2)
            rawCapture = PiRGBArray(camera, size=camera.resolution)
            for foo in camera.capture_continuous(rawCapture, format='bgr', use_video_port=True):
                cls.frameCV2 = foo.array
                rawCapture.truncate(0)
                if time.time() - cls.last_access > 10:
                    print('!BREAK!!')
                    break
        cls.thread = None

''' это было в примере
    @classmethod
    def _thread(cls):
        with picamera.PiCamera() as camera:
            # camera setup
            camera.resolution = (800, 600)
            camera.hflip = True
            camera.vflip = True

            # let camera warm up
            camera.start_preview()
            time.sleep(2)

            rawCapture = PiRGBArray(camera) # я добавил

            stream = io.BytesIO()
            for foo in camera.capture_continuous(stream, 'jpeg',
                                                 use_video_port=True):
                # store frame
                stream.seek(0)
                cls.frame = stream.read()

                # reset stream for next frame
                stream.seek(0)
                stream.truncate()

                # if there hasn't been any clients asking for frames in
                # the last 10 seconds stop the thread
                if time.time() - cls.last_access > 10:
                    break
        cls.thread = None
'''
