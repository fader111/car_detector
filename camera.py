#from time import time


#class Camera(object):
#    """An emulated camera implementation that streams a repeated sequence of
#    files 1.jpg, 2.jpg and 3.jpg at a rate of one frame per second."""
#
#    def __init__(self):
#        self.frames = [open(f + '.jpg', 'rb').read() for f in ['1', '2', '3']]
#
#    def get_frame(self):
#        return self.frames[int(time()) % 3]
#

import cv2

class Camera(object):
    def __init__(self):
        # Using OpenCV to capture from device 0(1). If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        try:
            self.video = cv2.VideoCapture(1)
            self.jpeg = cv2.imread("C:\\Users\\ataranov\\Projects\\flask-video-streaming-1\\1.jpg")
            cv2.imshow("q",self.jpeg)
        except:
            pass
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        try:
            success, image = self.video.read()
            # image = self.jpeg
            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the
            # video stream.
        #try:
            ret, jpeg = cv2.imencode('.jpg', image)
            cv2.waitKey(5)
            return jpeg.tostring()
        except:
            # jpeg = cv2.imread("C:\\Users\\ataranov\\Projects\\flask-video-streaming-1\\1.jpg")
            print ('no image...')
            # cv2.imshow("q",jpeg)
            # cv2.waitKey()
            return self.jpeg.tostring()