import time, threading
from pynput import mouse
from picamera2 import Picamera2, Preview, MappedArray
import os
from datetime import datetime as dt
import cv2

start = time.monotonic()
t0 = 0
t0c = True
t1 = 0
tn = 0

cap_rate = 10

slp_tm = round(1/cap_rate, 3)
print("sleep time = ",slp_tm)
trial_n = 1

colour = (0, 255, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2

def apply_timestamp(request):
    timestamp = dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)

def save_img(img_req):
    global folder_path, tn
    img_arr, tr_n, timestamp = img_req
    file_path = os.path.join(folder_path, 'GazeXBI_{}_trial_{}.jpg'.format(timestamp, tr_n))
    cv2.imwrite(file_path, img_arr)
    #tn = tn+1
    

def cap_img():
    global trial_n, t0, t0c
    """if t0c:
        t0 = time.monotonic()
        t0c = False"""
    img_arr = picam2.capture_array()
    timestamp = dt.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    tr_off = time.monotonic()
    return img_arr, trial_n, timestamp, tr_off

def on_click(x, y, button, pressed):
    global stop, session
    if pressed:
        if button==button.left:
            print("Starting recording")
            stop = False
        if button==button.right:
            print("Stopping recording") 
            stop = True
        if button==button.middle:
            print("Exiting")
            session = False
            return False

def runs():
    global slp_tm, start, stop, session, t0, t1, tn
    print()
    print()
    if not session:
        metadata = picam2.capture_metadata()
        print(metadata)
        #t1 = time.monotonic()
        #print(t1-t0)
        #print(tn)
        #print("avg fps = ", tn/(t1-t0))
        #picam2.stop_preview()
    if session:
        stt = (slp_tm-time.monotonic()+start)
        stt = round(stt, 3) if stt>0 else 0
        print(stt)
        time.sleep(stt)
        start = time.monotonic()
        if not stop:
            print("Capturing image")
            #cap_img()
            img_arr, trn, tmstp, off = cap_img()
            threading.Thread(target=save_img, args = ([img_arr, trn, tmstp], )).start()
           
        else:
            off = 0
            
        nxt = (slp_tm-time.monotonic()+start)
        nxt = round(nxt, 3)-0.008 if nxt>0 else 0
        #print(nxt*1000)
        time.sleep(nxt)
        print("Time of run = ",(time.monotonic()-start)*1000)
        runs()
        #threading.Timer(nxt, runs).start()
        
picam2 = Picamera2()
"""exp_tm = 3000
anlg_gn = exp_tm/1000"""
camera_config = picam2.create_still_configuration(controls={"FrameRate":50, "ExposureTime": 2000, "AnalogueGain": 20.0}, main={"size": (1280, 720)}, lores={"size": (640, 480)}, display="lores", buffer_count=10)
picam2.configure(camera_config)
picam2.pre_callback = apply_timestamp
#picam2.start_preview(Preview.QTGL)
picam2.start()

# Create a folder on the desktop with the current date if it doesn't exist
folder_path = os.path.expanduser('~/Desktop/{}'.format(dt.now().strftime('%Y-%m-%d')))
os.makedirs(folder_path, exist_ok=True)
os.chdir(folder_path)

stop = True
session = True

listener = mouse.Listener(on_click=on_click)
listener.start()

runs()
