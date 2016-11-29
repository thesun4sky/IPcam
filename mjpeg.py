import io
import os, signal, time
import random
from flask import Flask, render_template, Response, redirect
import picamera
import time
from PIL import Image
import numpy as np
from ipcam_config import load_config

width = 320 
height = 240
threshold = 20
minPixelsChanged = width * height * 40 / 100

prior_image = None
num = 0;
camera = picamera.PiCamera()
camera.resolution = (320, 240)
app = Flask(__name__)



@app.route('/')
def index():
    return redirect('/video_feed')



def save_pid():
    f = open('stream.pid', 'w')
    f.write(str(os.getpid()))
    f.close()

save_pid()

def get_frame():
    
    stream_jpg = io.BytesIO()
    camera.capture(stream_jpg, 'jpeg', use_video_port=True)
    stream_jpg.seek(0)
    
    return stream_jpg.read()

def detect_motion(camera):
    global prior_image
    stream_rgba = io.BytesIO()
    camera.capture(stream_rgba, 'rgba',True)
    stream_rgba.seek(0)
    if prior_image is None:
        prior_image = np.fromstring(stream_rgba.getvalue(), dtype=np.uint8)
        return False
    else:
        current_image = np.fromstring(stream_rgba.getvalue(), dtype=np.uint8)
        
        print("Compare")
                   
        data3 = np.abs(prior_image - current_image) 
        numTriggers = np.count_nonzero(data3 > threshold) / 4 

        print("Trigger cnt=",numTriggers)

        if numTriggers > minPixelsChanged:
              result = True
              print("result = True")
                   
        else:
              result = False

        prior_image = current_image
        return result
    
def gen():
    stream = picamera.PiCameraCircularIO(camera, seconds=10)
    camera.start_recording(stream, format='h264')
    try:
        while True:

            camera.wait_recording(1)
            if detect_motion(camera):
                print('Motion detected!')
                # fileName = time.strftime("%Y%m%d%H%M%S",time.localtime())
                # after_fileName = fileName + 'after.h264'
                # before_fileName = fileName + 'before.h264'
                # camera.split_recording(after_fileName)
                # stream.copy_to(before_fileName)
                stream.clear()
                while detect_motion(camera):
                    frame = get_frame()
                    yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    camera.wait_recording(1)
                print('Motion stopped!')
                
                #camera.split_recording(stream)
    finally:
        print('Fail!')
        camera.stop_recording()


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True)
