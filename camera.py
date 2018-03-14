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
    #video = cv2.VideoCapture("http://188.187.119.130:8080/hls/6176/5a2d33233089738ea8ff/playlist.m3u8?tcp")
    video = cv2.VideoCapture(1)
    def __init__(self):
        # Using OpenCV to capture from device 0(1). If you have trouble capturing
        # from a webcam, comment the line below out and use a video file
        # instead.
        try:
            #self.video.set(cv2.CAP_PROP_FRAME_WIDTH, 320) # это не работает
            #self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
            self.jpeg = cv2.imread("C:\\Users\\ataranov\\Projects\\flask-video-streaming-1\\1.jpg")
            #cv2.imshow("q",self.jpeg)
        except:
            pass
        # If you decide to use video.mp4, you must have this file in the folder
        # as the main.py.
        # self.video = cv2.VideoCapture('video.mp4')
    
    def __del__(self):
        pass #self.video.release()  переделать! чтобы работало корректно
    # @classmethod
    def get_frame(self):
    # def get_frame(cls):
        try:
            success, image = self.video.read()
            # We are using Motion JPEG, but OpenCV defaults to capture raw images,
            # so we must encode it into JPEG in order to correctly display the
            # video stream.
        #try:
            # print('get_frame') # вот это все тут не появляется и не работает... треды, или что виноваты. не понятно пока
            # image = cv2.resize(image,(480,320))
            ret, jpeg = cv2.imencode('.jpg', image)
            # cv2.imshow('qwe',image)
            # cv2.waitKey(2)
            return jpeg.tostring()
        except:
            # jpeg = cv2.imread("C:\\Users\\ataranov\\Projects\\flask-video-streaming-1\\1.jpg")
            print ('no image...')
            # cv2.imshow("q",jpeg)
            # cv2.waitKey()
            return self.jpeg.tostring()

    #@classmethod
    def get_frame_for_internal_proc(self):
        # print ('cls.video DO',cls.video)
        _,ret = self.video.read()
        # print ('cls.video POSLE',cls.video)
        return ret
