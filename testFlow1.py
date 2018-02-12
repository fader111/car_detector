
#from __future__ import print_function
import cv2, numpy as np
stringx=''
stringy=''
cap = cv2.VideoCapture(1)
_, prev= cap.read()
prev = cv2.cvtColor(prev, cv2.COLOR_BGR2GRAY)
gray=prev
cv2.imshow('gray', gray)
cv2.waitKey(1)
x, y, w, h = cv2.selectROI('gray', gray)
print('press r to get ROI')
cv2.rectangle(gray,(x,y),(x+w,y+h),255,2)
while cap.isOpened():
    color=127
    #print(x, y, w, h)
    ret, img = cap.read()
    #vis = np.zeros((6, 6), np.float32)
    #cv2.imshow('vis', vis)
    #cv2.waitKey(5)
    #img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    #img = vis_gr
    #####img = cv2.resize(img,(100,100))
    #print ('vis',vis)
    #gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #left = gray[:-5, :]
    #right = gray[5:, :]
    # cv2.imshow('right', right)
    # cv2.waitKey(5)
    grayROI = gray[y:y + h,x:x + w]
    prevROI = prev[y:y + h,x:x + w]
    #print ('grayROI',grayROI.shape)
    try:
        flow = cv2.calcOpticalFlowFarneback(grayROI, prevROI, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    except:
        print('grayROI=',grayROI)
    flowx = flow[:,:,0]
    flowy = flow[:,:,1]

    font = cv2.FONT_HERSHEY_SIMPLEX
    if flowx.mean()>0: title_x='R'
    else: title_x='L'
    if flowy.mean()>0: title_y='U'
    else: title_y='D'
    stringx_mes =title_x+str(abs(round(flowx.mean(),1)))
    #stringx =title_x+str(abs(round(flowx.mean(),1)))
    stringy_mes =title_y+str(abs(round(flowy.mean(),1)))
    #stringy =title_y+str(abs(round(flowy.mean(),1)))
    if abs(round(flowx.mean(),1))>0.3:
        stringx = stringx_mes
        color = 0
    if abs(round(flowy.mean(),1))>0.3:
        stringy = stringy_mes
        color=0
    cv2.rectangle(gray, (x, y), (x + w, y + h), color, 2)
    cv2.putText(gray, stringx, (5, 25), font, 0.8, 255, 2) # cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.putText(gray, stringy, (5, 45), font, 0.8, 255, 2) # cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 1.0, (0, 0, 0), thickness = 2, lineType=cv2.CV_AA)
    cv2.imshow('gray', gray)
    cv2.imshow('grayROI', grayROI)

    prev=gray
    c = cv2.waitKey(1)  # выход из цикла и закрытие окон по нажатию Esc
    if c == ord('r'):
        x, y, w, h = cv2.selectROI('gray', gray)
        flow=None
    if c == 27:
        cv2.destroyAllWindows()
        break
