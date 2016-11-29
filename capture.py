# -*- coding: utf-8 -*-
import signal, os, time
from picamera import PiCamera
from threading import Lock
from ipcam_config import load_config

lck = Lock()

cfg_dict = load_config()
resolution = cfg_dict['resolution']
annotate = cfg_dict['annotate']


def save_pid():
    f = open('capture.pid', 'w')
    f.write(str(os.getpid()))
    f.close()


def signal_handler(signum, frame):
    global resolution, annotate
    print 'Signal handler called with signal', signum
    # TODO: ipcam_config.py 가 새로 저장한 설정을 읽어서 설정 변수를 변경한다.
    cfg_dict = load_config()
    lck.acquire()
    resolution = cfg_dict['resolution']
    annotate = cfg_dict['annotate']
    lck.release()

signal.signal(signal.SIGUSR1, signal_handler)

# TODO: 이 프로세스의 PID를 특정 파일에 저장하여, 시그널을 보낼 프로그램(ipcam_config.py)이 PID를 알 수 있도록 한다.
#print 'PID:', os.getpid()
save_pid()

camera = PiCamera()

while True:
    # : 변경된 설정을 반영한다.
    lck.acquire()
    resolution_l = resolution
    annotate_l = annotate
    lck.release()

    # : 적당한 간격으로 캡쳐 한다.
    camera.resolution = resolution_l
    camera.annotate_text = annotate_l

    camera.capture('foo.jpg')
    time.sleep(5)
