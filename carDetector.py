#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
программа обнаруживает машины в рамках и меняет цвет рамки
версия где рамки - полигоны
заливаем черным все кроме рамки
обрезаем картинки по размеру рамки
недоработки : надо разделить выделение фореграунда и обучение фона.
первое нужно для каждого кадра, обучение фона - сильно реже.
сейчас есть компромис - первое и второе одновременно, раз в 100мс

доработка начата 23.10.2017, цель:
    - добавить тип рамки : присутствие,остановка
    - добавить детектирование направления движения в рамке
6.10 - направление в рамке берется из polygones.dat
каждую рамку делим на 4 части. при пересечении 2-х одновременно
на одной строне и потом 2-х одновременно на противоположной - проезд
в нужно мнаправлении считаем засчитан.

этот файл - бывший main.py переделанный для работы во flask с python3
'''
import cv2
import numpy as np
import os,sys,time,json
import requests
from multiprocessing import cpu_count
import threading
from threading import Timer
import threading
showMode = 1    # режим с показом картинок в gui (не работает с автозагрузкой в linux)
# больше не используется linWinMode = 0      # linux =0 Windows =1, в Main есть автоопределение.
# тестовые рамки для проверки, заменяются реальными по ходу программы
testRamki = [
            [
                [61, 325],
                [106, 277],
                [296, 464],
                [88, 539]
            ],
            [
                [344, 293],
                [370, 236],
                [698, 483],
                [427, 555]
            ],
            [
                [462, 101],
                [603, 150],
                [656, 257],
                [532, 247]
            ]
        ]
testMode = 0 # режим работы с тестовыми рамками - в нем не надо выдавать ничего на концентратор
dets = [] # массив экземпляров класса detector == рамки
ramki = [] # рамки которые считываются из файла polygones.dat
ramki4 = [] # массив рамок, где каждой из polygones соотв.4 рамки внутри.
ramkiModes = [] # режим работы рамок: 0 - присутствие, 1 остановка.
ramkiDirections = [] # направления в рамках для каждой [0,0,1,0] - 1 обозн. активно
ramkiEntrance =[] # массив для фиксации события въезда в рамку
ramkiMonitor = [] # массив для монироринга статуса больших рамок (введен после добавления направлений для отобр статуса большой рамки текстом)
colorStatus = [] # цвета рамок
height = 300 # px размер окна в котором происходит проверка не менять!!! чревато !!!
width = 400 # px ##
origWidth, origHeight = 800, 600 # размер окна браузера для пересчета
frameOverlapTres = 20 # frame overlap, %
frameOverlapHyst = 10 # frame hysteresis, %
learningRate = 0.0001 #0.00001 0.001 - это 13 секунд 0.0001 - 113 секунд !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
adaptLearningRateInit = 0.005 #0.005 это параметр на старте для времени обучения фона
adaptLearningRate =0 # при старте ему присваивается Init время и во время работы убавляется.
#fixLearningRate = 0.005 # параметр для рамок присутствия? пока не буду его. вместо него возьму adaptLearningRateInit
""" это старая ботва. пути перенесены в app.py 
polygonesFilePath = 'polygones.dat'
tsNumberMinuteFilePath = 'minTSNumber.dat'
tsNumberHourFilePath = 'hourTSNumber.dat'
"""
statusFilePath = 'status.dat'

tsNumbers = [] #  массив с количеством задетектированных тс
tsNumbersPrev = [] # массив с количеством тс предыдущего шага, чтобы его вычитать из текущего и находить разницу
tsNumbersInterval = [] # массив с количеством тс за интервал (10с)[a,b,c,d]
tsNumbersMinute = [] # массив с количеством тс с проездами за 1 интервал за минуту [[_,_,_][][][]]
tsNumbersMinuteSumm = [] # массив с количеством тс за минуту [[][][][]]
tsNumbersHour = [] # массив с количеством тс с проездами за 1 интервал за час [[_,_,_][][][]]
tsNumbersHourSumm =[] # массив с количеством тс за час [[][][][]]
tsCalcTimeInterval = 5 # раз в это число секунд считать тс может быть 1,2,3,4,5,6,10,15,20,30,60
maxNumberTS =10000 # если накопленное количество тс станет слишком большим, сбрасывать его.

# linImagePath = '/dev/shm/mjpeg/cam.jpg' # - это от старой версии кандидат на удаление
#linImagePath = 'C:/WebServers/home/savepic/www/pic.jpg' а это не вертать!
# класс вызывает функцию function с аргументами function, *args, **kwargs с интервалом interval
class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        #self.start()

    def _run(self):
        ##self.is_running = False
        self._start()
        self.function(*self.args, **self.kwargs)

    def _start(self):
        self._timer = Timer(self.interval, self._run)
        self._timer.start()

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        if self._timer:
            self._timer.cancel()
            self.is_running = False

    def isAlive(self):
        return self.is_running

# класс создает рамки, фон def getFgmask обновляет фон и вычисляет разницу с тек. кадром
# обновлен 6.11 - для понимания направления движеия каждая рамка поделена на 4. и все выше делается для каждой из 4-х.
# поделена линиями, соединяющими середины противоположных сторон.
class detector():
    def __init__(self, pict, frame, i):
        self.pict=pict
        self.borders = rectOverPolygon(frame)
        print ('self.borders =', self.borders)  ####################################################################
        self.mask = np.zeros((self.pict.shape[0], self.pict.shape[1]),
                             dtype=np.uint8)  # черная маска по размерам входной картинки
        adaptLearningRate = adaptLearningRateInit
        # self.bg = cv2.BackgroundSubtractorMOG2(500, 5, 0)  # аргументы (history, treshold, shadow) history не активно если юзаем learninRate
        # self.bg = cv2.BackgroundSubtractorMOG2(500, 5, 0)  # аргументы (history, treshold, shadow) history не активно если юзаем learninRate
        self.bg = cv2.createBackgroundSubtractorMOG2(500, 5, 0)  # аргументы (history, treshold, shadow) history не активно если юзаем learninRate
        #### Преобразование рамки в кооринаты обрезанного под нее окна
        print (i, 'frame =', frame)
        self.roi_corners = np.array([frame], dtype=np.int32)  # вершины рамки
        cv2.fillConvexPoly(self.mask, self.roi_corners, (255, 255, 255))  # из черной маски делаем черную с белой рамкой
        self.framedPict = cv2.bitwise_and(self.pict, self.mask)
        self.smallPict = self.framedPict[int(self.borders[1]):int(self.borders[3]), int(self.borders[0]):int(self.borders[2])]
        self.fgmask = self.bg.apply(self.smallPict, learningRate=adaptLearningRate)
        self.absMass = np.zeros((self.smallPict.shape[0], self.smallPict.shape[1]), np.uint8)  # матрица с нулями
        self.frameColor = 0  # (0, 0, 0)
        self.tss = 0

    def getFgmask(self,pict,frame, adaptLearningRate):
        self.pict = pict
        self.frameArea = polygonAreaCalc(frame)
        self.framedPict = cv2.bitwise_and(self.pict, self.mask)
        self.smallPict = self.framedPict[int(self.borders[1]):int(self.borders[3]), int(self.borders[0]):int(self.borders[2])]
        if (self.tss>time.time()): # на случай еслт time.time перейдет через 0 - не знаю может так быть, или нет
            self.tss=0
            print ('tss over!!!!!!!!!!!!')
        if ((time.time()-self.tss)>0.1):# для увеличения скорости прореживаем обновление фона
            self.fgmask = self.bg.apply(self.smallPict, learningRate=adaptLearningRate)
            self.fgmask = cv2.erode(self.fgmask, None)
            self.fgmask = cv2.dilate(self.fgmask, None)
            self.tss = time.time()
        #print ('tss', self.tss, time.time())
        #print ('dif',time.time()-self.tss)
        #cv2.imshow(str(self), self.fgmask)
        cv2.convertScaleAbs(self.fgmask, self.absMass)
        self.nonZeros = cv2.countNonZero(self.absMass)
        #print('self.frameArea',self.frameArea, self.nonZeros)
        #print (self.nonZeros%frameArea* frameOverlapTres)
        if (self.nonZeros/float(self.frameArea) * 100 > frameOverlapTres):
            self.frameColor = (255, 255, 0)
        elif (self.nonZeros/float(self.frameArea) * 100 < frameOverlapTres - frameOverlapHyst): # гистерезис в 10% чтобы рамка не дергалась
            self.frameColor = 0#(0, 0, 0)
        elif (self.nonZeros / float(self.frameArea) * 100 <= 0):  # на случай если порог установлен меньше гистерезиса
            self.frameColor = 0#(0, 0, 0)

def updTsNumsMinute(tsNumberMinuteFilePath): #обновляет по тикеру tsNumbers и tsNumbersPrev
    #print ('updTSMinute!!!!!!!!!!!!!!!!!!')
    for i,mem in enumerate(tsNumbers):
        tsNumbersInterval[i]=mem-tsNumbersPrev[i] # набиваем массив разницей за интервал (10 сек)
        tsNumbersPrev[i] = mem # переписываем в предыдущий число из текущего
        #try:
        #    pass
        #    assert type(tsNumbersMinute[i])==list,'tsNumbersMinute ='+str(tsNumbersMinute) ### tsNumbersMinute[i] обязательно должен быть массивом
        #except IndexError:
        #    print (IndexError,tsNumbersMinute)
        if (type(tsNumbersMinute[i])!=list):
            tsNumbersMinute[i]=[]
        tsNumbersMinute[i].append(tsNumbersInterval[i])  # добавляет в конец разницу за интервал
        tsNumbersMinute[i].pop(0) # и выкидывает первый в очереди
        tsNumbersMinuteSumm[i]=sum(tsNumbersMinute[i]) # кладет сумму в массив где копятся проезды за минуту
        if mem> maxNumberTS: # если количество посчитанных тс станет слишком велико, чтобы не отжирать память, сбрасывать его
            tsNumbers[i]-= maxNumberTS
            tsNumbersPrev[i]-= maxNumberTS
    #if (adaptLearningRate < 0.001):
        #os.system('cls')
        #print (tsNumbers  # = [])  # массив с количеством задетектированных тс
        #print (tsNumbersPrev  # = [])  # массив с количеством тс предыдущего шага, чтобы его вычитать из текущего и находить разницу
        #print (tsNumbersInterval  # = [])  # массив с количеством тс за интервал (10с)[a,b,c,d]
        #print (tsNumbersMinute  # = [])  # массив с количеством тс с проездами за 1 интервал за минуту [[_,_,_][][][]]
        #print (tsNumbersMinuteSumm  # = [])  # массив с количеством тс за минуту [[][][][]]
    writeFile(tsNumberMinuteFilePath, tsNumbersMinuteSumm)### запись файла в linux

def updTsNumsHour(tsNumberHourFilePath):
    #print ('updTSHour!!!!!!!!!')
    for i, mem in enumerate(tsNumbers):
        if (type(tsNumbersHour[i])!=list):
            tsNumbersHour[i]=[]
        tsNumbersHour[i].append(tsNumbersMinuteSumm[i])
        tsNumbersHour[i].pop(0)
        tsNumbersHourSumm[i]=sum(tsNumbersHour[i])
    #if (adaptLearningRate < 0.001):
        # os.system('cls')
        #print (tsNumbersHour)  # = []  # массив с количеством тс с проездами за 1 минуту [[_,_,_][][][]]
        #print (tsNumbersHourSumm)  # = []  # массив с количеством тс за час [[][][][]]
    # !!!!!!!!!!!!!!!!!writeFile(linTSNumberHourFilePath, tsNumbersHourSumm)### запись файла в linux
    writeFile(tsNumberHourFilePath, tsNumbersHourSumm)  ### запись файла в linux

def draw_str(dst, x, y, s):
    cv2.putText(dst, s, (x+1, y+1), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 0, 0), thickness = 2, lineType=1)
    # cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 255), lineType=cv2.CV_AA)
    cv2.putText(dst, s, (x, y), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 255), lineType=1)

def writeFile(filePath,status):
    with open(filePath,'w') as f:
        string = f.write(str(status))
        #print status,str(status)
    return 1

def writeFileColorStatus(filePath):
    with open(filePath,'w') as f:
        string = f.write(str(colorStatus))
        #print (colorStatus,str(colorStatus))
    return 1

def polygonAreaCalc(polygon):
    polygonArea = 0  # площадь полигона
    polyLen = len(polygon)
    # print ('n=',n)
    for i in range(polyLen):
        x = polygon[i][0]
        if i == 0:
            y = polygon[polyLen - 1][1]
            y1 = polygon[i + 1][1]
        elif i == polyLen - 1:
            y = polygon[i - 1][1]
            y1 = polygon[0][1]
        else:
            y = polygon[i - 1][1]
            y1 = polygon[i + 1][1]
        polygonArea += x * (y - y1)
        #print (x * (y - y1))
    return abs(polygonArea) / 2

def rectOverPolygon(polygon):
    x1,y1=x2,y2=polygon[0]
    for i in range (len(polygon)):
        if polygon[i][0] < x1: x1 = polygon[i][0]
        if polygon[i][1] < y1: y1 = polygon[i][1]
        if polygon[i][0] > x2: x2 = polygon[i][0]
        if polygon[i][1] > y2: y2 = polygon[i][1]
    return x1,y1,x2,y2

def readPolyFile(polygonesFilePath): # считывание файла с полигонами
    #time.sleep(0.1)
    #global origWidth, origHeight,ramki,ramkiModes,ramkiDirections,linPolygonesFilePath
    global origWidth, origHeight, testMode

    try:
        with open(polygonesFilePath, 'r') as f:
            jsRamki = json.load(f)
            ramki = jsRamki.get("polygones", testRamki)
            origWidth, origHeight = jsRamki.get("frame", (800, 600))  # получаем размер картинки из web интрефейса
            ramkiModes = jsRamki.get("ramkiModes", [0,0,0,0]) # по дефолту все рамки - в режиме присутствие
            ramkiDirections = jsRamki.get("ramkiDirections", [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]) # дефолт - нет направлений.
            testMode = 0
            
    except Exception as Error: # если рамки не считались, и подставились тестовые, работает криво - рамки каждый раз масштабируются, как это поправить, пока не знаю.
        print (u'считать рамки не удалось, пришлось подставить тестовые..', Error)
        ramki = testRamki
        ramkiModes = [0,0,0,0]
        ramkiDirections = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        testMode = 1

    # масштабируем рамки
    #dets = []  # будущие экземпляры класса detector
    # в цикле создаем рамки и передем им данные рамок из веб интерфейса
    for i in range(len(ramki)):
        xRate = round(origWidth/float(width))              # соотношение сторон по x картинки с web и картинки в питоне
        yRate = round(origHeight/float(height))            # то-же по y
        ###print (ramki[i] , 'i=',i, 'origWidth',origWidth, 'origHeight',origHeight)
        for j in range(len(ramki[i])):
            ramki[i][j][0] = ramki[i][j][0]/xRate     # масштабирование всех рамок
            ramki[i][j][1] = ramki[i][j][1]/yRate
    return ramki,ramkiModes,ramkiDirections


# функция делает 4 рамки из одной. входной аргумент однако - весь массив рамок
def make4RamkiFrom1(ramki):
    # вход ramki[i]=[[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
    # выхлоп ramki4[i] = [[[x0,y0],[x1,y1],[x2,y2],[x3,y3]],[вторая внутр. рамка],(третья....] т.е. [i][внурт рамка 1-4][угол][кордината x или y]
    ramki4=[[[[0,0] for k in range(4)] for j in range(4)] for i in range(len(ramki))] # нулями ее забить выхлоп при старте
    for i in range(len(ramki)):
        x0= ramki4[i][0][0][0]= ramki[i][0][0]
        y0= ramki4[i][0][0][1]= ramki[i][0][1]
        x1= ramki4[i][1][1][0]= ramki[i][1][0]
        y1= ramki4[i][1][1][1]= ramki[i][1][1]
        x2= ramki4[i][2][2][0]= ramki[i][2][0]
        y2= ramki4[i][2][2][1]= ramki[i][2][1]
        x3= ramki4[i][3][3][0]= ramki[i][3][0]
        y3= ramki4[i][3][3][1]= ramki[i][3][1]
        # находим середины строн, они-же координаты углов внутренних рамок
        x01= ramki4[i][0][1][0]= ramki4[i][1][0][0]= (x0+x1)/2  #x0+(x1-x0)/2
        y01= ramki4[i][0][1][1]= ramki4[i][1][0][1]= (y0+y1)/2
        x12= ramki4[i][1][2][0]= ramki4[i][2][1][0]= (x1+x2)/2
        y12= ramki4[i][1][2][1]= ramki4[i][2][1][1]= (y1+y2)/2
        x23= ramki4[i][2][3][0]= ramki4[i][3][2][0]= (x2+x3)/2
        y23= ramki4[i][2][3][1]= ramki4[i][3][2][1]= (y2+y3)/2
        x30= ramki4[i][3][0][0]= ramki4[i][0][3][0]= (x3+x0)/2
        y30= ramki4[i][3][0][1]= ramki4[i][0][3][1]= (y3+y0)/2
        xm = ramki4[i][0][2][0]= ramki4[i][1][3][0]=ramki4[i][2][0][0]=ramki4[i][3][1][0]=(x01+x23)/2
        ym = ramki4[i][0][2][1]= ramki4[i][1][3][1]=ramki4[i][2][0][1]=ramki4[i][3][1][1]=(y01+y23)/2
        #print ("ramki[i]",ramki[i])
    return ramki4

