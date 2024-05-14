import time, threading
from picamera2 import Picamera2, Preview, MappedArray
import os
from datetime import datetime as dt
import cv2
import socket
import pandas as pd


# initializing global variables
start = time.monotonic()
start_trial = 0

# Variables to test runtime of functions
t0 = 0
t0c = True
t1 = 0
tn = 0

#frame capture recording - Initialising csv file for image info storage
columns = ['trial_number', 'file_name', 'time_from_trial_start', 'touch']
fcr = pd.DataFrame(columns = columns)
fc_data = 'FrameCapture_Data_GazeXBI_{}.csv'.format(start)
tch_info = []
tch_flag = 0

# Initialising trial flags 
stop = True
session = True

# Set number of images captured per second (cap_rate), exposure time (exp_time) and analogue gain (anl_gain) here
# NOTE - set the cap_rate such that 1/cap_rate, which is the sleep time (slp_tm; see line 40), is 
# at least 10 milliseconds more than exposure time to buffer any jitters in run time of other functions
# NOTE - exposure time is in microseconds. For milliseconds, divide by 1000.
# NOTE - the lower the exposure time, the greater the analogue gain needed. 
cap_rate = 10
exp_time = 6000 
anl_gain = 10.0

# Sleep time - the function pauses for this much time depending on how many images you wish to capture per second. 
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

def csv_init():
    # To initialise new csv file
    global columns, fcr, fc_data, start
    fcr = pd.DataFrame(columns = columns)
    fc_data = 'FrameCapture_Data_GazeXBI_{}.csv'.format(start)

def listen2mac():
    # Modifying trial flags with information received from mworks(via python)
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

def cap_img():
    #capturing jpg 
    global t0, t0c
    img_arr = picam2.capture_array()
    timestamp = dt.now().strftime('%Y%m%d%H%M%S%f')[:-3]
    tr_off = time.monotonic()
    return img_arr, timestamp, tr_off

# Initialising picamera
picam2 = Picamera2()
camera_config = picam2.create_still_configuration(controls={"FrameRate":50, "ExposureTime": exp_time, "AnalogueGain": anl_gain}, main={"size": (1280, 720)}, lores={"size": (640, 480)}, display="lores", buffer_count=10)
picam2.configure(camera_config)
picam2.pre_callback = apply_timestamp
picam2.start()

# Create a folder on the desktop with the current date if it doesn't exist
folder_path = os.path.expanduser('~/Desktop/{}'.format(dt.now().strftime('%Y-%m-%d')))
os.makedirs(folder_path, exist_ok=True)
os.chdir(folder_path)

# Running listining to trial flags on separate thread to run the image capture in uninterrupted manner (avoids time spent in initialising upon every new trial)
threading.Thread(target=listen2mac).start()

while True:
    if not session: 
        metadata = picam2.capture_metadata()
        print(metadata)
        print("ending")
        break
    if session:
        stt = (slp_tm-time.monotonic()+start)
        stt = round(stt, 3) if stt>0 else 0
        time.sleep(stt)
        start = time.monotonic()
        if not stop:
            print("Capturing image")
            img_arr, tmstp, off = cap_img()
            threading.Thread(target=save_img, args = ([img_arr, tmstp], )).start() #Saving is done on a separate thread to prevent it from holding up the code
        else:
            off = 0
            
        nxt = (slp_tm-time.monotonic()+start)
        nxt = round(nxt, 3) if nxt>0 else 0
        time.sleep(nxt)
        print("Time of run = ",(time.monotonic()-start)*1000, end = '\r')



