import socket
import threading
import time
import subprocess
import os

# Define the path to your scripts and the conda environment
conda_env = "dlc-live"
script_to_run = "DLClive-Test.py"

# Command to open a new terminal, activate conda, and run the Python script
command = f'''
osascript -e 'tell application "Terminal" to do script "cd /Users/cnl/Desktop/XBI_GazeML/ && conda activate {conda_env} && python {script_to_run}"'
'''

# Execute the command to open a new terminal and run the script
subprocess.run(command, shell=True)

time.sleep(10)
#command = "cd /Users/cnl/Desktop/XBI_GazeML/ && conda activate dlc-live && python3 DLCLive-Test.py""


IP =  socket.gethostname()
#IP = '169.254.129.153'  # IP address of the server
PORT = 5000  # Port number on which the server is listening

stop = False

for i in range(0,120):
    try:
        # Create a socket object
        SOCKET = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Attempt to connect to the server
        SOCKET.connect((IP, PORT))
        print(f"Connected to {IP}:{PORT}")

        try:
            SOCKET.bind((IP, PORT))
            print(f"Socket was free, connection established.")
            break
        except socket.error as e:
            if e.errno == socket.errno.EADDRINUSE:
                print(f"Port {port} is already in use. Terminating connection.")
                SOCKET.close()  # Close the connection if the port is in use
                continue

        stop = False
        break

    except (socket.error, ConnectionRefusedError):
        print(f"Connection failed. Retrying in 1 second...")

        # Wait for 1 second before retrying
        time.sleep(1)

def start():
    
    # Get the trial number from then
    trial_number = getvar('TRIAL_start')
    print(trial_number)
    
    # ==============================================================    
    #  THIS IS THE MESSAGE THAT WILL BE SENT TO THE SERVER
    message = f'start {trial_number}'
    SOCKET.send(message.encode())
    response = SOCKET.recv(1024).decode()
    print('R:', response)
    # ============================================================== 
    
def pause_video():
    tch = getvar('IO_background')
    """if tch:
        touch_info(1)
        return"""
    message = f'pause'
    SOCKET.send(message.encode())
    response = SOCKET.recv(1024).decode()
    print('R:', response)

def stop_video():
    tch = getvar('IO_background')
    """if tch:
        touch_info(1)
        return"""
    message = f'stop'
    SOCKET.send(message.encode())
    response = SOCKET.recv(1024).decode()
    print('R:', response)

def touch_info(stop = 0):
    '''touch_x = getvar('TOUCH_x_dva')
    touch_x = getvar('TOUCH_x_dva')'''
    message = f'touched'
    """if stop==1:
        message = message + ' stop'"""
    SOCKET.send(message.encode())
    response = SOCKET.recv(1024).decode()
    print('R:', response)

def exit():
    global SOCKET, stop
    while True:
        try:
            data = SOCKET.recv(1024).decode()
            if data == 'bye':
                stop = True# receive response# show in
        except ConnectionResetError:
            continue

  # connect to the server

x = threading.Thread(target = exit, daemon = True)
x.start()

if stop:
    client_socket.close() 



