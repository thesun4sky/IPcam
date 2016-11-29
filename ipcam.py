
from flask import Flask, send_file, render_template, request, Response, redirect
import os, signal

def read_capture_pid():
    with open('capture.pid', 'r') as f:
        line = f.readline()
        return int(line)
    return -1


def read_stream_pid():
    with open('stream.pid', 'r') as f:
        line = f.readline()
        return int(line)
    return -1

def check_pid():
    cap_pid = read_capture_pid()
    if cap_pid > 0:
        os.kill(cap_pid, signal.SIGKILL)
    str_pid = read_stream_pid()
    if str_pid > 0:
        os.kill(str_pid, signal.SIGKILL)
    f = open('capture.pid', 'w')
    f.write(str('0'))
    f.close()
    f = open('stream.pid', 'w')
    f.write(str('0'))
    f.close()
    return -1

check_pid()

from ipcam_config import save_config, load_config
import io
import random
import time
from PIL import Image
import numpy as np
import subprocess

app = Flask(__name__)

@app.route('/')
def index() :
    check_pid()
    return render_template('index.html')

@app.route('/cam')
def cam():
    subprocess.Popen(["python capture.py"],shell=True);
    cfg_dict = load_config()
    return render_template('config.html', annotate_text=cfg_dict['annotate'],
        resolution=cfg_dict['resolution']) # config.html은 templates/config.html 에 위치해야 함.



def gen():
    while True:
        frame = get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.route('/config')
def config():
    resolution = request.args.get('resolution', '')
    annotate = request.args.get('annotate', '')
    print resolution, annotate
        
    # TODO: resolution, annotate 설정을 특정 파일에 저장한다. 저장 방법은 xml이나 pickle 등을 사용
    save_config(resolution, annotate)

    # 캡쳐 프로그램이 설정을 다시 읽도록 SIGUSR1 시그널을 보낸다.
    cap_pid = read_capture_pid()
    if cap_pid > 0:
        os.kill(cap_pid, signal.SIGUSR1)
        return 'OK'
    else:
        return 'Failed! - no capture.py is running'

@app.route('/capture')
def capture():
    return send_file('foo.jpg') # 캡쳐 프로그램이 캡쳐한 파일 전송

    
@app.route('/stream')
def stream():
    subprocess.Popen(["python mjpeg.py"],shell=True);
    time.sleep(3);
    return render_template('stream.html');

if __name__ == '__main__':
    app.run('0.0.0.0')
