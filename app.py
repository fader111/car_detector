#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os, socket
from flask import Flask, render_template, Response, request, json
from carDetector import *

app = Flask(__name__)

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR) # выключает информационные сообщения flask оставляет только аварийные

winMode=0
showMode = 0
ipStatus = {"ip": '192.168.0.100',
            "mask": '255.255.255.0',
            "gateway": '192.168.0.1',
            "hub": '192.168.0.101'
            }
linPath = 'dt2/' # путь к файлу проекта в linux
winPath = ''     # путь к файлу проекта в windows
path = ''        # рабочий путь к файлам проекта

polygonesFilePath = 'polygones.dat'
tsNumberMinuteFilePath = 'minTSNumber.dat'
tsNumberHourFilePath = 'hourTSNumber.dat'

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
              b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
# вызывается при старте и при изменении настроек IP в форме - устанавливает в linux новые
def putIPsettingsLinux(ip, mask, gateway):
    ipComm = os.popen("sudo ifconfig eth0 " + ip + " netmask " + mask)
    routComm = os.popen("sudo route del default")
    gwComm = os.popen("sudo route add default gw " + gateway)
    ipComm.read()
    routComm.read()
    gwComm.read()
    return 0

@app.route('/sendPolyToServer', methods=['GET', 'POST']) # это вызывается при нажатии на кнопку редактировать и отсылает полигоны на сервер
def sendPolyToServer():
    filePath = path+'polygones.dat'
    if request.method == 'POST':
        print("request.get_data (poly)== ", request.get_data())
        polygones = request.form["req"]
        print ('polygones=',polygones)
    try:
        with open(filePath, 'w') as f: #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            f.write(polygones)  # Пишем данные полигонов в файл.
    except:
        print(u"Не удалось сохранить файл ipconf.dat")
    print('settings saved!')
    return json.dumps('Polygones sent to server...')

@app.route('/getPolyFromServer', methods=['GET', 'POST'])
def getPolyFromServer():
    #print('polygonesFilePath = ',polygonesFilePath)
    polygones = None
    filePath = path + 'polygones.dat'
    print('filePath = ',path + 'polygones.dat')
    try:
        with open(filePath, 'r') as f: #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            polygones = f.read()  # Пишем данные полигонов в файл.
    except:
        print(u"Не удалось прочитать файл ipconf.dat")
    #print('считанные рамки = ',polygones)
    # return json.dumps(ramki)
    return json.dumps(polygones)

@app.route('/sendIpSettingsToServer', methods=['GET', 'POST']) # это вызывается при нажатии на кнопку на форме и сохраняет параметры ip на сервере
def sendIpSettingsToServer():
    global ipStatus # спорно, не нужно тут
    filePath=path+'ipconf.dat'
    if request.method == 'POST':
        print("request.get_data", request.get_data())
    ip = request.form['ip']
    mask = request.form['mask']
    gateway = request.form['gateway']
    hub = request.form['hub']
    print('from python: ip', ip,'  mask',mask, '  gateway',gateway,'  hub',hub)
    if not winMode:
        with open(filePath, 'w') as f:  # Открываем на чтение и запись.
            f.write(json.dumps({'ip': ip, 'mask': mask, 'gateway': gateway, 'hub': hub}))  # Пишем данные в файл.
            print('settings saved!')
        putIPsettingsLinux(ip, mask, gateway)
    return json.dumps({'ip': ip,'mask':mask, 'gateway':gateway,'hub':hub})

@app.route('/showStatus', methods=['POST'])
def showStatus():
	#if request.method == 'POST':
	#	print('request.get_data = ',request.get_data())
	return json.dumps(colorStatus)

@app.route('/', methods=['GET', 'POST'])
def index():
    global ipStatus
    if winMode: # в windows варианте все для теста
        ipStatus = {
            "ip": socket.gethostbyname_ex(socket.gethostname())[2][2], # выдает второй по счету ip адрес среди прочих
            "mask":"255.255.255.0", #это просто заглушки для теста
            "gateway":"192.168.0.1",
            "hub": "192.168.0.38"
        }
    else:
        ipStatus = {"ip":get_ip(),
                    "mask":get_mask(),
                    "gateway":get_gateway(),
                    "hub":get_hub()
                   }
    # print request.form.get['X']
    if request.method == 'POST':
        print("request.get_data", request.get_data())
        # по имени определяем от какой формы прилетело
        if b"btn1" in request.get_data(): # если в тексте ответа есть кнопка первой формы, обращаемся к полям отвеченного
            ipStatus['ip'] = str(request.form['ip'])
            ipStatus['mask'] = str(request.form['mask'])
            ipStatus['gateway'] = str(request.form['gateway'])
            ipStatus['hub'] = str(request.form['hub'])
            print ("['ip'] =",ipStatus['ip'])
            print ("['mask'] =",ipStatus['mask'])
            print ("['gateway'] =",ipStatus['gateway'])
            print ("['hub'] =",ipStatus['hub'])
        if b"btn2" in request.get_data():
            pass
    return render_template('index.html',title = '1',ipStatus = ipStatus)
def get_ip():
    #ifconfig eth0 | grep 'inet' |grep -v '127.0.0.1'| grep -v 'inet6'|cut -d: -f2|awk '{print $2}' так работает ниже - нет
    #return (os.system("/sbin/ifconfig  | grep 'inet '| grep -v '127.0.0.1' | cut -d: -f2 | awk '{ print $1}'"))
    res=os.popen("/sbin/ifconfig eth0 | grep 'inet' |grep -v '127.0.0.1'| grep -v 'inet6'|cut -d: -f2|awk '{print $2}'")
    return (res.read())
def get_mask():
    res = os.popen("/sbin/ifconfig eth0 | grep 'inet' |grep -v '127.0.0.1'| grep -v 'inet6'|cut -d: -f2|awk '{print $4}'")
    return (res.read())
def get_gateway():
    res = os.popen("netstat -rw | grep default | awk '{if (NR==1) print$2}'")
    return (res.read())
def get_hub():
    filePath = path+'ipconf.dat'
    data = {'hub':'0.0.0.0'} # на случай, если файл не откроется
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print (u'не удалось считать файл насяйникэ мана!')
    return data['hub'] # возвращает hub
def ipSetup(): # считывает настройки сети для интерфейса eth0 из файла и сует их в linux
    filePath = path + 'ipconf.dat'
    data ={"gateway": "192.168.0.1", "hub": "192.168.0.38", "ip": "192.168.0.31", "mask": "255.255.255.0"}
    try:
        with open(filePath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print(u'Не удалось считать файл ipconf.dat ...')
    putIPsettingsLinux(data['ip'], data['mask'], data['gateway'])



def updatePolyFromServer(polygonesFilePath): #обновляет в периоде полигоы с сервера
    #print("Update!!!")
    lock.acquire() # блокировка главного треда вызвавшего эту хрень, на время выполнения обновления полиогонов
    global ramki,ramkiModes, ramkiDirections, dets,ramki4,dets4,adaptLearningRate, pict, ramkiMonitor, colorStatus, \
        colorStatusPrev, tsNumbers,tsNumbersPrev, tsNumbersInterval,tsNumbersMinute,tsNumbersMinuteSumm, tsNumbersHour, \
        tsNumbersHourSumm
    ramkiUpd,ramkiModesUpd,ramkiDirectionsUpd = readPolyFile(polygonesFilePath)
    #print ("from updatePolyFromServer rm   - ", ramki)
    #print ("from updatePolyFromServer rmupd- ", ramkiUpd)
    if (ramki != ramkiUpd or ramkiModes != ramkiModesUpd or ramkiDirections != ramkiDirectionsUpd ):
        #проверяем новые рамки на наличие отрицательных значений
        print ("nesovpad!!!") #,ramki[3], ramkiUpd[3]
        for i in ramkiUpd:
            for j in i:
                for k in j:
                    if k<=0:
                        print ('negative Coordinates in polygones!!!!')
                        lock.release()  # отпуск блокировки
                        return # если в рамках есть ошибка, нех ничо обновлять
        ramki = ramkiUpd[:]
        ramkiModes = ramkiModesUpd[:]
        ramkiDirections = ramkiDirectionsUpd[:]
        dets = []  # будущие экземпляры класса detector
        # в цикле создаем рамки и передем им данные рамок из веб интерфейса
        # print ('len(pict) === ',len(pict))
        #for i in range(len(ramki)):
        #    dets.append(detector(pict, ramki[i], i))
        #    ###print (ramki[i])
        ramki4 = make4RamkiFrom1(ramki)
        dets4 = [[] for i in range(len(ramki))]  # подготовили массив для детекторов X4

        for ramka in range(len(ramki)):  # в dets4 будут лежать объекты класса
            for ramki1_4 in range(4):  # создание экземпляров класса детекторов по 4 в каждой рамке
                print ("ramki[ramka][ramki1_4]",ramki[ramka][ramki1_4])
                dets4[ramka].append(detector(pict, ramki4[ramka][ramki1_4], ramka))
                ###print (ramki[i])
        adaptLearningRate = adaptLearningRateInit
        ramkiMonitor = [0 for i in ramki]  # и все остальные рабочие массивы надо изменять, т.к. поменялось количество рамок
        colorStatus = [0 for i in ramki]  # массив в котором лежат цвета рамок текущего цикла
        colorStatusPrev = [0 for i in ramki]  # массив в котором лежат цвета рамок предыдущего цикла
        tsNumbers = [0 for i in ramki]  # массив в котором лежит числ проехавших тс
        tsNumbersPrev = [0 for i in ramki]  # массив в котором лежит числ проехавших тс за предыдущий промежуток времени
        tsNumbersInterval = [0 for i in ramki] # и т.д. см инициализацию вначале программы
        tsNumbersMinute = [0 for i in ramki]
        tsNumbersMinuteSumm = [0 for i in ramki]
        tsNumbersHour = [0 for i in ramki]
        tsNumbersHourSumm = [0 for i in ramki]
        print ('adaptLearningRate-------------', adaptLearningRate)
    lock.release() #отпуск блокировки


def flaskThread():
    app.run(host='0.0.0.0', port=80, debug=False, threaded=True, use_reloader=False)
    print ("app started!")

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

if __name__ == '__main__':
    #showMode = 1
    if 'win' in sys.platform:
        from camera import Camera
        winMode = 1
        path = winPath
        print ("Windows mode")
    else:
        from camera_pi import Camera
        winMode = 0
        path = linPath
        polygonesFilePath = path+'polygones.dat'
        tsNumberMinuteFilePath = path+'minTSNumber.dat'
        tsNumberHourFilePath = path+'hourTSNumber.dat'
        statusFilePath = linPath + statusFilePath
        ipSetup() # вызоd программы для установки ip адреса - на винде не делаем..
        print ("Linux mode")

    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True,use_reloader=False)
    cameraThread = threading.Thread(target=flaskThread).start()

    ### прошел запуск web сервера в отдельном потоке, началась работа детектора ###
    for param in sys.argv: # запуск проги в режиме визуализации
        if param == 'vis':
            print ('work in visual mode')
            showMode = 1
    lock = threading.RLock() #будем блокировать треды
    #ramki,ramkiModes,ramkiDirections = readPolyFile(polygonesFilePath)
    rt = RepeatedTimer(tsCalcTimeInterval, updTsNumsMinute, tsNumberMinuteFilePath)#!!!!!!!!! вызывает функцию которая будет обновлять массив количества проехавших с отсчетами за интервал
    rtUpdPolyFromServer = RepeatedTimer(5, updatePolyFromServer, polygonesFilePath)
    rth = RepeatedTimer(60,updTsNumsHour, tsNumberHourFilePath) # вызывает функцию, которая будет обновлять минутные отсчеты и формировать данные о кол-ве тс за час
    rtUpdStatusForWeb =  RepeatedTimer(0.4, writeFileColorStatus,*[statusFilePath]) # обновляем статус для web сервера раз в 400 мс !!!!!!!!!!!!!!!!!!!!!!!проблема с мс
    rt.start() # запустить таймер
    rth.start()# ...
    rtUpdPolyFromServer.start()
    rtUpdStatusForWeb.start()
    ramki, ramkiModes, ramkiDirections = readPolyFile(polygonesFilePath)
    print ('ramki = ',ramki)
    print ('ramkiModes = ',ramkiModes)
    print ("ramkiDirections=",ramkiDirections)
    #print 'cpu_count = ', cpu_count()
    adaptLearningRate = adaptLearningRateInit
    #print ('origWidth origHeight= ', origWidth, origHeight)
    if winMode:
        #capture = cv2.VideoCapture(1)   # на рабочем (1)
        #capture = cv2.VideoCapture('C:/Users/ataranov/test.avi')
        #camera2 = Camera() # создаем новый экземпляр
        # _,pict = Camera.video.read()  #вариант для Windows
        pict = Camera().get_frame_for_internal_proc() # вызов класс метода без создания экземпляра. чистая блажь, можно сделать обычным способом с экземпляром и методом
        #print('pict =',pict.schape)
        #pict = Camera().get_frame()
    else:
        pict = Camera().get_frame_for_internal_proc() # для линукса
        print('After else!!!')
        #pict = cv2.imread('dt2/1.jpg')
    ######pict = cv2.imread('cam.jpg')
    print('tut!')
    pict = cv2.cvtColor(pict, cv2.COLOR_BGR2GRAY)
    pict = cv2.resize(pict, (width,height))
    # считывание файла с полигонами
    dets = []  # будущие экземпляры класса detector  dets ниже везде заменть в while
    # в цикле создаем рамки и передем им данные рамок из веб интерфейса
    # обновлено 6.11 из каждой рамки надо сделать 4
    # сначала сфрмировать новые рамки - в 4 раза больше.
    ramki4 = make4RamkiFrom1(ramki)
    dets4=[[] for i in  range(len(ramki))] # подготовили массив для детекторов X4

    for ramka in range(len(ramki)): # в dets4 будут лежать объекты класса
        for ramki1_4 in range(4): # создание экземпляров класса детекторов по 4 в каждой рамке
            #print ("ramki[ramka][ramki1_4]",ramki[ramka][ramki1_4])
            dets4[ramka].append(detector(pict, ramki4[ramka][ramki1_4],ramka))
        ###print (ramki[i])
    learningRateInc = learningRate /100.0
    ts2 = time.time() # time stamp для обновления статуса рамок для web сервера
    ts3 = time.time() # time stamp для обновления рамок при изменении их с web интерфейса
    treadSendPost = None
    ramkiEntrance = [[0,0,0,0] for i in ramki] # массив для фиксации события въезда в рамку с определенного направления.
    #ramkiPassEvents=[0 for i in ramki]          # массив для фиксации события проезда через рамку ( в будущем можно доделать его до собитий по каждому направлению)
    ramkiMonitor = [0 for i in ramki]
    tsNumbers = [0 for ii in ramki]  # количество задетектированных тс [0,0,0,0] для 4-х рамок
    colorStatus = tsNumbers[:]   # клон tsNumbers в котором лежат цвета рамок текущего цикла
    colorStatusPrev = tsNumbers[:]   # клон tsNumbers в котором лежат цвета рамок предыдущего цикла
    tsNumbersPrev = tsNumbers[:]  # массив с количеством тс предыдущего шага, чтобы его вычитать из текущего и находить разницу
    tsNumbersInterval = tsNumbers[:]  # массив с количеством тс за интервал (10с)[a,b,c,d]
    tsNumbersMinute = tsNumbers[:]  # массив с количеством тс с проездами за 1 интервал за минуту [[_,_,_][][][]]
    tsNumbersMinuteSumm = tsNumbers[:]  # массив с количеством тс за минуту [10,20,30,40]
    tsNumbersHour = tsNumbers[:] # ... за час
    tsNumbersHourSumm = tsNumbers[:] # ... сумма за час
    numberOfInterval = int(60/tsCalcTimeInterval) # количество интервалов в минуте для подсчета тс
    for i in range(len(tsNumbers)): # по количеству рамок
        tsNumbersMinute[i]=[0 for ii in range(numberOfInterval)]
    for i in range(len(tsNumbers)):# по количеству рамок
        tsNumbersHour[i]=[0 for ii in range(60)]
    #print ("tsNumbersMinute",tsNumbersMinute)

    # это нужно для подсчета тс - при переходе цвета рамки из 0 в 1 - кол-во тс+=1
    #print (" ts numbers = ",tsNumbers)
    # ------ Устанавливаем ловушку для исключений ---
    # def excepthook(exc_type, exc_value, exc_traceback):
    #     # log.error(exc_type, exc_value, exc_traceback)
    #     with open('ErrLog','a') as Erf:
    #         Erf.write("{0}\n{1}\n{2}\n\n".format(exc_type, exc_value, exc_traceback))
    # sys.excepthook = excepthook
    # -----------------------------------------------
    while 1:#capture.isOpened(): # восстановить для линукса!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        lock.acquire()  # блокировка треда, на время выполнения обновления рамок
        # print ('while start')
        ts = time.time()  # засекли время начала цикла
        if (learningRate < adaptLearningRate):  # если стартовое время обучения меньше финального, уменьшаем его постепенно
            adaptLearningRate -= learningRateInc
        # пробуем считать картинку
        try:
            if winMode :
                #_, pict = capture.read()  # старый вариант для Windows со встроенной камерой в ноутбук
                # _,pict = Camera.video.read()
                pict = Camera().get_frame_for_internal_proc()
            else:
                pict = Camera().get_frame_for_internal_proc()
                #pict = cv2.imread('dt2/1.jpg')
        except:
            print (u'Выпали нах!')
            continue # если считать картинку не удалось, переходим к след итерации цикла
        time.sleep(0.02) # искусственная шняга иначе до weba вообще дело не доходит.
        #try:
        #    pass #pict.shape
            # print('pict=',pict)
        #except:
        #    continue
        #print ('imSape Type=',type(pict))
        #print('len pict=', len(pict))
        pict = cv2.cvtColor(pict, cv2.COLOR_BGR2GRAY)
        pict = cv2.resize(pict, (width, height))
        #print ('len(ramki)=',len(ramki))
        # if(1):
        try:
            for i in range (len(ramki)): # проходим по всем рамкам и назначаем цвет, и считаем ТС
                # dets[i].getFgmask(pict,ramki[i], adaptLearningRate) # экземпляры класса detector == рамки
                # print ("ramkiModes=",ramkiModes[i])
                # суть алгоритма: берем направление из ramkiDirections. Если текущее ==1, то формирууем событие "въезд". Это сработка 2-х
                # рамок на въезде без сработки на выезде. если было событие въезд, далее контролируем событие выезд для этого направления:
                # сработка хотя-бы одной выездной зоны. если случилосЬ, красим, иначе нет. так, перебираем по всем направлениям.
                for j in range (4): # перебираем по каждой из 4-х рамок внутри одной большой
                    if ramkiModes[i]==0: # режим работы рамки "присутствие"
                    # экземпляры класса detector == рамки разбитые на 4 части:
                        dets4[i][j].getFgmask(pict,ramki4[i][j], adaptLearningRateInit) # с постоянным соотношением времени обучения фона равного начальному.
                    else:
                        dets4[i][j].getFgmask(pict,ramki4[i][j], adaptLearningRate) # либо с изменяемым.
                    if showMode:
                        cv2.polylines(pict, [np.array(ramki4[i][j], np.int32)], 1, dets4[i][j].frameColor, 2)
                        dets4[i][j].winName = "bkg" + str(i)+str(j)
                        ##print ('#####',i,'=',dets[i].borders[3]- dets[i].borders[0],dets[i].fgmask.shape)
                        # cv2.imshow(dets4[i][j].winName,dets4[i][j].fgmask) #показывает на отдельных картинках фореграунд маску.

                # фиксируем событие "въезд в рамку с определенного направления"
                if ramkiDirections[i][0]: # заданное направление в рамке условно 'вверх', !!!!! под вопросом нужно-ли оно!!!
                    if ((dets4[i][2].frameColor or dets4[i][3].frameColor) and not (dets4[i][0].frameColor or dets4[i][1].frameColor)):
                        ramkiEntrance[i][2] = 1 # событие въезд условно 'снизу' установлено
                        #print ("sobitie vezd snis!",i)
                    if not (dets4[i][2].frameColor or dets4[i][3].frameColor):
                        #print ("len ramkiEntrance = ", len(ramkiEntrance))
                        ramkiEntrance[i][2] = 0 # событие въезд условно 'снизу' сброшено
                        #print ("sobitie vezd snis sbros!!!", i)
                if ramkiDirections[i][1]: # заданное направление в рамке вправо
                    if ((dets4[i][3].frameColor or dets4[i][0].frameColor) and not (dets4[i][1].frameColor or dets4[i][2].frameColor)):
                        #print ("sobitie vezd sleva!", i)
                        ramkiEntrance[i][3] = 1 # въезд слева
                    if not (dets4[i][3].frameColor or dets4[i][0].frameColor):
                        ramkiEntrance[i][3] = 0  # событие въезд 'слева' сброшено
                if ramkiDirections[i][2]: # заданное направление в рамке условно 'вниз',
                    if ((dets4[i][0].frameColor or dets4[i][1].frameColor) and not (dets4[i][2].frameColor or dets4[i][3].frameColor)):
                        ramkiEntrance[i][0] = 1 # событие въезд условно 'сверху'
                    if not (dets4[i][0].frameColor or dets4[i][1].frameColor):
                        ramkiEntrance[i][0] = 0  # событие въезд 'сверху' сброшено
                if ramkiDirections[i][3]: # заданное направление в рамке влево
                    if ((dets4[i][1].frameColor or dets4[i][2].frameColor) and not (dets4[i][3].frameColor or dets4[i][0].frameColor)):
                        ramkiEntrance[i][1] = 1 # въезд справа
                    if not (dets4[i][1].frameColor or dets4[i][2].frameColor):
                        ramkiEntrance[i][1] = 0  # событие въезд 'справа' сброшено

                # фиксируем событие "проезд рамки в определенном направлении" в списке ramkiMonitor
                if (ramkiDirections[i][0] and ramkiEntrance[i][2] and (dets4[i][0].frameColor or dets4[i][1].frameColor)):
                    ramkiMonitor[i] = 1  # если направление вверх, был въезд снизу, и потом проезд других рамок, то сработка
                    #print ("Proehali!!! vverh",i)

                if (ramkiDirections[i][1] and ramkiEntrance[i][3] and (dets4[i][1].frameColor or dets4[i][2].frameColor)):
                    ramkiMonitor[i] = 1  # если направление вправо, был въезд слева, и потом проезд других рамок, то сработка

                if (ramkiDirections[i][2] and ramkiEntrance[i][0] and (dets4[i][2].frameColor or dets4[i][3].frameColor)):
                    ramkiMonitor[i] = 1  # если направление вниз, был въезд сверху, и потом проезд других рамок, то сработка

                if (ramkiDirections[i][3] and ramkiEntrance[i][1] and (dets4[i][3].frameColor or dets4[i][0].frameColor)):
                    ramkiMonitor[i] = 1  # если направление влево, был въезд справа, и потом проезд других рамок, то сработка

                # если хоть одна рамка беленькая, то вся рамка сработанная, иначе переодим в несработанное состояние
                if not (dets4[i][0].frameColor or dets4[i][1].frameColor or dets4[i][2].frameColor or dets4[i][3].frameColor):
                    ramkiMonitor[i] = 0
                # если направлений нет, или их 4, рамка срабатывает при сработке любой внутренней
                if not (ramkiDirections[i][0] or ramkiDirections[i][1] or ramkiDirections[i][2] or ramkiDirections[i][0]):
                    if (dets4[i][0].frameColor or dets4[i][1].frameColor or dets4[i][2].frameColor or dets4[i][3].frameColor):
                        ramkiMonitor[i] = 1
                    else:
                        ramkiMonitor[i]=0
                if (ramkiDirections[i][0] and ramkiDirections[i][1] and ramkiDirections[i][2] and ramkiDirections[i][0]):
                    if (dets4[i][0].frameColor or dets4[i][1].frameColor or dets4[i][2].frameColor or dets4[i][3].frameColor):
                        ramkiMonitor[i] = 1
                    else:
                        ramkiMonitor[i]=0
                if not (testMode): # текущий статус рамок обновляем только в случае, если
                    if (ramkiMonitor[i] > 0):
                        colorStatus[i] = 1
                        if colorStatusPrev[i] == 0:  # при переходе цвета рамки 0->1 прибавляем
                            tsNumbers[i] += 1
                    else:
                        colorStatus[i] = 0
                    colorStatusPrev[i] = colorStatus[i]  # текущее состояние цвета рамки передаем предыдущему, и переходим к следующей итерации цикла

                draw_str(pict, int(ramki[i][3][0]) + 5, int(ramki[i][3][1]) - 5, str(tsNumbers[i]))  # показывает количество тс проехавших в рамке за время работы программы (надо сделать чтоб за минуту) - dN/dt
                if ramkiModes[i]==0:
                    currentState = "P"
                else:
                    currentState = "S"
                draw_str(pict, int(ramki[i][0][0]) + 5, int(ramki[i][0][1]) + 25, currentState)  # показывает режим работы рамки проезд или остановка
                # print ("ramkiModes[i]",ramkiModes[i])
                draw_str(pict,int(ramki[i][0][0]) + 5, int(ramki[i][0][1]) + 45, str(ramkiMonitor[i]))
                colorStatusPrev[i] = colorStatus[i]  # текущее состояние цвета рамки передаем предыдущему, и переходим к следующей итерации цикла
        except IndexError:
           print (IndexError)
        #    print ('len(dets4)',len(dets4))
        # print ("ramki==",ramki)
        #except:
        #    print ("exception", ramki)
            #updatePolyFromServer()
        #print ('colorStatus',colorStatus)
        # обновляем статус для web сервера раз в 400 мс
        #!!!!!!!!!!!!!!!!!!! начать отсюда - вынести нах в отдельную ф-цию !!!!! if (int(1000*(time.time()-ts2)>400)):
            ######################## Закоменчено для работы в Windows #########################writeFile(linStatusFilePath,colorStatus)
        #    ts2 = time.time()
        if showMode:
            #print ('adaptLearningRate',adaptLearningRate)
            draw_str(pict, 20, 25, str(int(1000*(time.time()-ts)))) # индикация времени выполнения цикла в мс
            draw_str(pict, 75, 25, "LearnRate "+str(round(adaptLearningRate,5)))
            cv2.imshow("input", pict)
    # print ("tsNumbers---",tsNumbers)
        # передача состояний рамок на концентратор методом POST
        #print ('colorStatus',colorStatus)
        #requests.post('http://192.168.1.254:80/detect', json={"cars_detect": colorStatus}).text
        #treadSendPost = threading.Thread(target=sendingStatusToHub, args=(colorStatus))
        #treadSendPost.start()
	#print (str(int(1000*(time.time()-ts))))
	#os.system('clear')
        c = cv2.waitKey(1) # выход из цикла и закрытие окон по нажатию Esc
        if c == 27:
            rt.stop()
            rth.stop()
            rtUpdPolyFromServer.stop()
            rtUpdStatusForWeb.stop()
            # shutdown_server() # убивает насмерть web сервант однако не работает требует HTTP запроса
            #if cameraThread :
            #    cameraThread.stop()
            #    cameraThread = None # поток это не убивает
            break
        lock.release()  # роспуск блокировки
    cv2.destroyAllWindows()
    #if treadSendPost and treadSendPost.is_alive :
    #    treadSendPost.terminate()







	

