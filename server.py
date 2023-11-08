import socket
import threading
from time import sleep
import sys
import utils

# Keep the control of the message that will be sent to all the clients 
def msgGenerator():
    global lyric_line, music_name, musics
    while True:
        for line in musics:
            if '#' in line:
                music_name = line.replace('#','').strip()
                lyric_line = '*Now playing {} ...\n'.format(music_name)
            else:
                lyric_line = line
            sleep(sleep_interval) # Interval of gerneration of the messages

# Get the message that will be sent to client from a global variable
def getMessage():
    global music_name, lyric_line
    msg = music_name + '|' + lyric_line
    return msg

# Thread that will handle a single Client will run this function
def comunica_cliente(client_addr, data):
    seq = 0 # Sequence number of the messages
    while True:
        # If the client closed the connection
        if str(client_addr) in RUNF and RUNF[str(client_addr)]:
            RUNF[str(client_addr)] = False
            break
        msg = getMessage()
        seq = seq + 1
        utils.send(sock, client_addr, (seq, msg))
        sleep(sleep_interval)

    print("{} Closed connection to the server...".format(client_addr))
    print("Finishing thread...")
    print("TOTAL CLIENTS ",threading.active_count()-2)

# ===================== Start code =====================
RUNF = {} # This dictionary makes the control of witch client thread is active
lyric_line = ''
music_name = ''
musics_file = open("musicas.txt", "r")
musics = musics_file.readlines()
musics_file.close()

# If the sleep interval is defined, it will be used. Defaul is 2 seconds...
if len(sys.argv) > 1:
    sleep_interval = float(sys.argv[1])
else:
    sleep_interval = 2

UDP_IP = "127.0.0.1" # Loopback
UDP_PORT = 6454 # Server UDP port
server_addr = (UDP_IP, UDP_PORT)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(server_addr)

# Start a new thread that will start to generate the messages
thread = threading.Thread(target=msgGenerator, args=())
thread.start()

while True:
    try: # Principal thread wait to receive connection request from clients
        data, client_addr = sock.recvfrom(20)
    except:
        data = False
    
    # If one of the clients want to close the connection 
    if data == b'bye':
        print("Received {} message from {}".format(data, client_addr))
        RUNF[str(client_addr)] = True
    # A new client desires to start a connection with the server
    elif data == b'Hello':
        print('Got connection request from {} with message {}. Creating a new thread...'.format(client_addr, data))
        thread = threading.Thread(target=comunica_cliente, args=(client_addr, data))
        thread.start() # Starts a new thread that will comunicat to each client
        print("TOTAL CLIENTS ",threading.active_count()-2)

    sleep(0.1)

print("Closing server...")