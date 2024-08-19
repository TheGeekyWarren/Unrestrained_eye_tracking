import time
from dlclive import DLCLive, Processor
import cv2
import numpy as np
import pandas as pd
import threading
import socket
from datetime import datetime

host = socket.gethostname()
port = 5000  # socket server port number

try_again = False

server_socket = socket.socket() # instantiate
while True:  # connect to the server
	if try_again:
		print("Trying again")
	try:
	    server_socket.bind((host, port))
	    print(f"Socket was free, connection established.")
	    break
	except socket.error as e:
	    if e.errno == socket.errno.EADDRINUSE:
	        print(f"Port {port} is already in use. Terminating connection.")
	        server_socket.close()  # Close the connection if the port is in use
	        try_again = True

server_socket.listen(2)
conn, address = server_socket.accept()
print("Connection from: " + str(address))

cond = False
stop = False
trial = 0
feat_loc = np.empty((0,56, 3), float)
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
file_name = f"/Users/cnl/Desktop/XBI_GazeML/monkey_facedata_{current_time}.csv"

def start():
	global cond 
	cond = True 

def stop_video():
	global cond 
	cond = False 
    
def eyesinframe(loc):
	#1 HeadTop_Mid
	#2 RightEarTop_Join
	#3 RightEarTop_High
	#4 RightEar_Outer
	#5 RightEarBottom_Low
	#6 RightEarBottom_Join
	#7 RightEar_Tragus
	#8 OutlineTop_Mid
	#9 OutlineTop_Right
	#10 OutlineRight_Brow
	#11 OutlineRight_Indent
	#12 OutlineRight_Cheek
	#13 OutlineRight_Mouth
	#14 OutlineChin_Mid
	#15 OutlineLeft_Mouth
	#16 OutlineLeft_Cheek
	#17 OutlineLeft_Indent
	#18 OutlineLeft_Brow
	#19 OutlineTop_Left
	#20 LeftEarTop_Join
	#21 LeftEarTop_High
	#22 LeftEar_Outer
	#23 LeftEarBottom_Low
	#24 LeftEarBottom_Join
	#25 LeftEar_Tragus
	#26 Eyes_MidPoint
	#27 RightEye_Inner------
	#28 RightEye_Top--------
	#29 RightEye_Outer------
	#30 RightEye_Bottom-----
	#31 RightEye_Pupil-----------
	#32 RightEye_Highlight
	#33 LeftEye_Inner-------
	#34 LeftEye_Top---------
	#35 LeftEye_Outer-------
	#36 LeftEye_Bottom------
	#37 LeftEye_Pupil------------
	#38 LeftEye_Highlight
	#39 RightBrow_Outer
	#40 RightBrow_Top
	#41 RightBrow_Inner
	#42 Brow_MidPoin
	#43 LeftBrow_Inner
	#44 LeftBrow_Top
	#45 LeftBrow_Outer
	#46 RightNostrils_Top
	#47 RightNostrils_Bottom
	#48 LeftNostrils_Bottom
	#49 LeftNostrils_Top
	#50 NostrilsTop_Centre
	#51 UpperLip_Centre
	#52 LipsMeet_Centre
	#53 LowerLip_Centre
	#54 MidPoint_Nostrils_Mouth
	#55 Neck_Nape
	print(loc)
	idx = [31, 37]
	tidx = [i-1 for i in idx]
	feats = np.take(loc, tidx, axis=0)
	check = True
	for i in feats:
		if i[2]<0.9:
			check = False
	return int(check)


def incomming():
	global conn, stop, trial
	while True:
		try:
			data = conn.recv(1024).decode()
			if not data:
				continue
			if data.startswith('start'):
				trial = int(data.split(' ')[1])
				start()
			if data == 'pause':
				stop_video()
			if data == 'stop':
				stop = True
			if stop:
				break
			response='Message received'
			conn.send(response.encode())
		except ConnectionResetError:
			print('Client closed')
			break
		time.sleep(0.1)

def exit():
	data = 'bye'
	conn.send(data.encode())


dlc_proc = Processor()
#dlc_model = 'DLC-YR-2024-01-10_test/dlc-models/iteration-0/DLC_GazeRGB_mobilenet_v2_1.0_iteration-0_shuffle-3/'
#dlc_model = 'DLC-YR-2024-01-10_test/dlc-models/iteration-0/DLC_GazeRGB_mobilenet_v2_0.35_iteration-0_shuffle-8/'
dlc_model = 'DLC-YR-2024-01-10_test/dlc-models/iteration-0/DLCJan10-trainset95shuffle1/train'
dlc_live = DLCLive(dlc_model, processor=dlc_proc)

cap = cv2.VideoCapture(0)
cap.set(3,320)
cap.set(4,240)

if not cap.isOpened():
	print("Cannot open camera")
	exit()

print('camera opened')

while True:
	ret, frame = cap.read()
	if ret:
		dlc_live.init_inference(frame)
		break
	else:
		continue

print('dlc initiated')

def run():
	global file_name
	columns = [
    'HeadTop_Mid', 'RightEarTop_Join', 'RightEarTop_High', 'RightEar_Outer', 'RightEarBottom_Low', 
    'RightEarBottom_Join', 'RightEar_Tragus', 'OutlineTop_Mid', 'OutlineTop_Right', 'OutlineRight_Brow', 
    'OutlineRight_Indent', 'OutlineRight_Cheek', 'OutlineRight_Mouth', 'OutlineChin_Mid', 'OutlineLeft_Mouth', 
    'OutlineLeft_Cheek', 'OutlineLeft_Indent', 'OutlineLeft_Brow', 'OutlineTop_Left', 'LeftEarTop_Join', 
    'LeftEarTop_High', 'LeftEar_Outer', 'LeftEarBottom_Low', 'LeftEarBottom_Join', 'LeftEar_Tragus', 
    'Eyes_MidPoint', 'RightEye_Inner', 'RightEye_Top', 'RightEye_Outer', 'RightEye_Bottom', 'RightEye_Pupil', 
    'RightEye_Highlight', 'LeftEye_Inner', 'LeftEye_Top', 'LeftEye_Outer', 'LeftEye_Bottom', 'LeftEye_Pupil', 
    'LeftEye_Highlight', 'RightBrow_Outer', 'RightBrow_Top', 'RightBrow_Inner', 'Brow_MidPoin', 'LeftBrow_Inner', 
    'LeftBrow_Top', 'LeftBrow_Outer', 'RightNostrils_Top', 'RightNostrils_Bottom', 'LeftNostrils_Bottom', 
    'LeftNostrils_Top', 'NostrilsTop_Centre', 'UpperLip_Centre', 'LipsMeet_Centre', 'LowerLip_Centre', 
    'MidPoint_Nostrils_Mouth', 'Neck_Nape'
	]

	# Create multilevel columns for facial landmarks
	multi_columns_landmarks = pd.MultiIndex.from_product([columns, ['x-coordinates', 'y-coordinates', 'confidence']])

	# Create multilevel columns for the 'data' section
	multi_columns_data = pd.MultiIndex.from_product([['data'], ['date-time', 'trial-no', 'eyes-in-frame']])

	# Combine the 'data' columns and the facial landmarks columns
	all_columns = multi_columns_data.append(multi_columns_landmarks)

	# Create an empty DataFrame with the combined multilevel columns
	df = pd.DataFrame(columns=all_columns)

	print('run started')
	global cap, feat_loc, cond, dlc_live, stop, trial
	print(cond)
	while True:
		if stop:
			now=time.strftime('%j%m%y%H%M')
			file = f'EyeTrack_{now}'
			np.save(file, feat_loc)
			break
		if not cond:
			continue
		t1 = time.monotonic()
		ret, frame = cap.read()
		if not ret:
			print('cant receive frame')
			return
		loc = dlc_live.get_pose(frame)
		eif = eyesinframe(loc)
		deets = np.reshape(np.array([time.strftime('%j%m%y %H%M%S.%f'), trial, eif]), (1,3))
		locndeets = np.reshape(np.append(deets,loc, axis = 0), (1,56,3))
		flattened_array = locndeets.flatten()
		#feat_loc = np.append(feat_loc, locndeets)
		
		df.loc[len(df)] = flattened_array
		#new_df = pd.DataFrame(feat_loc, columns=all_columns) 
		#df.loc[len(df)] = row_data
		#df = pd.concat([df, new_df], ignore_index=True)
		df.to_csv(file_name, index=False)
		print(eif)
		print(time.monotonic()-t1)
		print()
		#cv2.imshow('Frame', frame)
		 
		
print('run_initiating')
x = threading.Thread(target = incomming, daemon = True)
x.start()

run()

cap.release()
exit() 
conn.close()
print(feat_loc)
cv2.destroyAllWindows()
