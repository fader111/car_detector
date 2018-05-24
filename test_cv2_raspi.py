import cv2
video = cv2.VideoCapture(0)
print('video ', video )
# video = cv2.VideoCapture(1)
# print('video 1', video )
# video = cv2.VideoCapture(2)
# print('video 2', video )
# while video.isOpened():
while True:
    success, image = video.read()
    print('succ, image',success, image)
    cv2.imshow('pic',image)
    key = cv2.waitKey(2)
    if key == 27:
        break

