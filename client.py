import socket
import sys, os
import threading
from getkey import getkey
import utils

# A thread will check if user press "q" or "space-bar" keys
def check_input():
    global close_client_flag, operation
    while True:
        key = getkey()
        if key == 'q': # Close clients connection and ends execution
            close_client_flag = True
            break
        elif key == ' ': # switch to show music name mode or show music lyrics
            os.system('clear')
            operation = True if operation == False else False

# Check is the command line is correct
if len(sys.argv) != 2:
    print('Correct usage: python3 client.py <Port number>')
    exit(1)

# Clear console terminal
os.system('clear')

UDP_IP = "127.0.0.1"
UDP_PORT = 6454 # UDP port to the server

close_client_flag = False
operation = False
last_seq_number = 0
lost_pkg_counter = 0
outOrderPkg = 0

dest = (UDP_IP, UDP_PORT)
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Socket
UDP_PORT_RECV = int(sys.argv[1])
try:
    sock.bind((UDP_IP, UDP_PORT_RECV))
except: # Check if UDP port is already in use
    print('Error: Porta expecificada já em uso, por favor informe outra.')
    exit(1)

# Send connection request
print("Sending Hello message...")
sock.sendto(b'Hello', dest)

# Start a thread to check user's input in a non-bloquing way 
thread = threading.Thread(target=check_input, args=())
thread.start()

while True:
    # Wait for the package from the server
    data = utils.receiv(sock)
    seq_number = data[0]
    msg = data[1]
    
    # Accounts the number of packages that arrived out of order
    if seq_number > last_seq_number:
        if seq_number != last_seq_number + 1:
            lost_pkg_counter += (seq_number - last_seq_number) - 1 # Accounts the number of lost packages.
        
        music_name = msg.split('|')[0]
        line = msg.split('|')[1]

        # Operation specifies if just the music name is shown of if the lyric line is shown
        if operation:
            os.system('clear')
            print('Now playing '+ music_name)
        else:
            # Means that is a new music, so console needs to be cleaned 
            if '*' not in line:
                print(line)
            else:
                os.system('clear')
                print('==============================================')
                line = line.replace('*', '')
                print(line)
                print('==============================================')
        last_seq_number = seq_number
    else:
        outOrderPkg += 1

    # Close the connection with the server
    if close_client_flag:
        message = b'bye'
        print('Sending bye message...')
        sock.sendto(message, dest)
        sock.close()
        break   

# Print report
print("Closing connection to the server...")
print('Total Out of Order Packets received: {}'.format(outOrderPkg))
print('Total lost packages count: {}'.format(lost_pkg_counter))
exit(0)