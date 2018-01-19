#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os, socket
from flask import Flask, render_template, Response, request
import camera
import subprocess
winMode=0
# emulated camera
# from camera import Camera

# Raspberry Pi camera module (requires picamera package)
# from camera_pi import Camera

app = Flask(__name__)

# @app.route('/')
# def index():
#     """Video streaming home page."""
#     return render_template('index.html')

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if winMode: # в windows варианте все для теста не стоит тут искать правды. чисто просто проверить
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
    return ("")
if __name__ == '__main__':
    if 'win' in sys.platform:
        from camera import Camera
        winMode = 1
        print ("Windows mode")
    else:
        from camera_pi import Camera
        winMode = 0
        print ("Linux mode")
    #try:
    #app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
    #except:
    #    pass





	

