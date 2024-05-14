import time, threading
#from pynput import mouse
from picamera2 import Picamera2, Preview, MappedArray
import os
from datetime import datetime as dt
import cv2
import socket
import pandas as pd


# initializing global variables
start = time.monotonic()
start_trial = 0

t0 = 0
t0c = True
t1 = 0
tn = 0

#frame capture recording
columns = ['trial_number', 'file_name', 'time_from_trial_start', 'touch']
fcr = pd.DataFrame(columns = columns)
fc_data = 'FrameCapture_Data_GazeXBI_{}.csv'.format(start)
tch_info = []
tch_flag = 0

def csv_init():
    global columns, fcr, fc_data, start
    fcr = pd.DataFrame(columns = columns)
    fc_data = 'FrameCapture_Data_GazeXBI_{}.csv'.format(start)

stop = True
session = True

cap_rate = 10

slp_tm = round(1/cap_rate, 3)
print("sleep time = ",slp_tm)
trial_n = 0

#Font for timestamp on each image
colour = (0, 255, 0)
origin = (0, 30)
font = cv2.FONT_HERSHEY_SIMPLEX
scale = 1
thickness = 2

# Configuration
SERVER_IP = '0.0.0.0'  # Use 0.0.0.0 to accept connections from any IP
SERVER_PORT = 5000  # Define the port

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Check if a socket is already open on the specified port
socket_in_use = False
try:
    server_socket.bind((SERVER_IP, SERVER_PORT))
except socket.error as e:
    if e.errno == 98:
        socket_in_use = True
        print('Address already in use. Closing the existing socket.')

# Close the existing socket if found
if socket_in_use:
    server_socket.close()

# Create a new socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the IP address and port
server_socket.bind((SERVER_IP, SERVER_PORT))

# Listen for incoming connections
server_socket.listen(1)
print('Server listening on {}:{}'.format(SERVER_IP, SERVER_PORT))

def listen2mac():
    global stop, session, trial_n, start_trial, fcr, start, fc_data, tch_info, tch_flag
    while True:
        # Accept a client connection
        client_socket, client_address = server_socket.accept()
        print('Connected to client:', client_address)

        while True:
            try:
                # Receive data from the client
                data = client_socket.recv(1024).decode()
                if not data:
                    break  # If no data received, break the loop

                # Process the received data
                print('Received from client:', data)

                if data.startswith('start'):
                    # Extract the trial number from the message
                    trial_n = data.split(' ')[1]

                    # Start recording the video
                    stop = False
                    start_trial = time.monotonic()
                    
                elif data.startswith('touched') and tch_flag==0:
                    #tch_info = [data.split(' ')[1], data.split(' ')[2]]
                    tch_info = [1]
                    print(tch_info)
                    tch_flag=1

                elif data.startswith('stop') or data.endswith('stop'):
                    # Stop recording the video
                    stop = True
                    fcr.to_csv(fc_data)
                    if int(trial_n)%20 == 0:
                        csv_init()
                    start_trial = 0 
                    
                else:
                    print('Invalid command')

                # Send a response back to the client
                response = 'Message received: {}'.format(data)
                client_socket.send(response.encode())

            except ConnectionResetError:
                # If the client connection is abruptly closed, handle the exception
                print('Client connection closed unexpectedly')
                break

        # Close the client connection
        client_socket.close()

    # Close the server socket (will not be reached in this example)
    server_socket.close()
    print("Session closing")
    session = False


def apply_timestamp(request):
    #applzing timestamp on each image
    timestamp = dt.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    with MappedArray(request, "main") as m:
        cv2.putText(m.array, timestamp, origin, font, scale, colour, thickness)

def save_img(img_req):
    #Saving the array of image captured from camera into a .jpg file
    global folder_path, trial_n, fcr, start_trial, tch_info, tch_flag
    img_arr, timestamp = img_req
    file_path = os.path.join(folder_path, 'GazeXBI_{}_trial_{}.jpg'.format(timestamp, trial_n))
    fcr.loc[len(fcr)] = [trial_n, file_path, (time.monotonic() - start_trial), tch_info]
    if tch_flag==1:
        tch_info = []
        tch_flag=0
    cv2.imwrite(file_path, img_arr)
    #tn = tn+1
    

def cap_img():
    #capturing jpg 
    global t0, t0c
    """if t0c:
        t0 = time.monotonic()
        t0c = False"""
    img_arr = picam2.capture_array()
    timestamp = dt.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    tr_off = time.monotonic()
    return img_arr, timestamp, tr_off

'''
def on_click(x, y, button, pressed):
    global stop, session, trial_n
    if pressed:
        if button==button.left:
            print("Starting recording")
            stop = False
            trial_n = trial_n+1
        if button==button.right:
            print("Stopping recording") 
            stop = True
        if button==button.middle:
            print("Exiting")
            session = False
            return False
'''


"""
def runs():
    global slp_tm, start, stop, session, t0, t1, tn
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
        time.sleep(stt)
        start = time.monotonic()
        if not stop:
            print("Capturing image")
            #cap_img()
            img_arr, tmstp, off = cap_img()
            threading.Thread(target=save_img, args = ([img_arr, tmstp], )).start()
           
        else:
            off = 0
            
        nxt = (slp_tm-time.monotonic()+start)
        nxt = round(nxt, 3) if nxt>0 else 0
        #print(nxt*1000)
        time.sleep(nxt)
        print("Time of run = ",(time.monotonic()-start)*1000, end = '\r')
        runs()
        #threading.Timer(nxt, runs).start()
"""

#camera = CAM()
'''
def start_video(trial):
    """
    Start recording a video with the specified trial number.

    :param trial: Trial number
    """
    # Get the current date and time
    timestamp = dt.now().strftime('%Y%m%d%H%M%S')

    # Create a folder on the desktop with the current date if it doesn't exist
    folder_path = os.path.expanduser('~/Desktop/{}'.format(dt.now().strftime('%Y-%m-%d')))
    os.makedirs(folder_path, exist_ok=True)

    # Start recording a video with the filename based on the timestamp and trial number
    file_path = os.path.join(folder_path, 'GazeXBI_{}_trial_{}.h264'.format(timestamp, trial))

    camera.resolution = (1280, 720)
    camera.framerate = 25

    camera.start_recording(file_path)
    print('Video recording started:', file_path)

def stop_video():
    """
    Stop the video recording.
    """
    if camera.recording:
        camera.stop_recording()
        print('Video recording stopped')
    else:
        print('No video recording to stop')
        '''

picam2 = Picamera2()
"""exp_tm = 3000
anlg_gn = exp_tm/1000"""
camera_config = picam2.create_still_configuration(controls={"FrameRate":50, "ExposureTime": 6000, "AnalogueGain": 10.0}, main={"size": (1280, 720)}, lores={"size": (640, 480)}, display="lores", buffer_count=10)
picam2.configure(camera_config)
picam2.pre_callback = apply_timestamp
#picam2.start_preview(Preview.QTGL)
picam2.start()

# Create a folder on the desktop with the current date if it doesn't exist
folder_path = os.path.expanduser('~/Desktop/{}'.format(dt.now().strftime('%Y-%m-%d')))
os.makedirs(folder_path, exist_ok=True)
os.chdir(folder_path)

threading.Thread(target=listen2mac).start()
#listener = mouse.Listener(on_click=on_click)
#listener.start()

while True:
    if not session:
        metadata = picam2.capture_metadata()
        print(metadata)
        print("ending")
        break
        #t1 = time.monotonic()
        #print(t1-t0)
        #print(tn)
        #print("avg fps = ", tn/(t1-t0))
        #picam2.stop_preview()
    if session:
        stt = (slp_tm-time.monotonic()+start)
        stt = round(stt, 3) if stt>0 else 0
        time.sleep(stt)
        start = time.monotonic()
        if not stop:
            print("Capturing image")
            #cap_img()
            img_arr, tmstp, off = cap_img()
            threading.Thread(target=save_img, args = ([img_arr, tmstp], )).start()
           
        else:
            off = 0
            
        nxt = (slp_tm-time.monotonic()+start)
        nxt = round(nxt, 3) if nxt>0 else 0
        #print(nxt*1000)
        time.sleep(nxt)
        print("Time of run = ",(time.monotonic()-start)*1000, end = '\r')
        #threading.Timer(nxt, runs).start()



