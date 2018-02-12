# -*- coding: utf-8 -*-
import os,json,cv2,time

def get_hub():
	data = {'hub':'0.0.0.0'} 
	try:
		with open("./ipconf.dat", "r") as f:
			data = json.load(f)
	except:
		print (u'no file!')	
	return data['hub']

#print (os.getcwd())
#lis = os.listdir(os.getcwd())
#print (lis)
#if 'ipconf.dat' in lis:
#	print ("est file!")

#print (get_hub())

# проверяем что быстрее imdecode или imencode

# считываем картинку jpeg 
#jpeg = cv2.imread("C:\\Users\\ataranov\\Projects\\flask-video-streaming-1\\1.jpg")
jpeg = cv2.imread("qq.jpg")
ntimes =100
print u'начали кодировать ',ntimes
ts = time.time()
for i in range(ntimes):
	_,buff = cv2.imencode('.jpg',jpeg)
	#print 'jpeg',len(jpeg)
	#print '\n\r\n\r\n\r'
	#print 'buff',len(buff)
	#cv2.imshow('q',jpeg)
	#cv2.waitKey(1)
tspend = time.time()-ts
print u'кодирование time spend ',tspend	

print u'начали декодировать ',ntimes
ts = time.time()
for i in range(ntimes):
	#_,buff = cv2.imencode('.jpg',jpeg)
	image = cv2.imdecode(buff, cv2.CV_LOAD_IMAGE_COLOR)
	#print 'jpeg',len(jpeg)
	#print '\n\r\n\r\n\r'
	#print 'buff',len(buff)
	#cv2.imshow('q',jpeg)
	#cv2.waitKey(1)
tspend = time.time()-ts
print u'декод time spend ',tspend	
cv2.destroyAllWindows()
