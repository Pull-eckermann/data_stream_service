import socket
import sys, os
import threading
from getkey import getkey
import utils

def check_input():
    global close_client_flag, operation
    while True:
        key = getkey()
        if key == 'q':
            close_client_flag = True
            break
        elif key == ' ':
            os.system('clear')
            operation = True if operation == False else False

if len(sys.argv) != 2:
    print('Uso correto: python3 client.py <Número da porta>')
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
except:
    print('Erro: Porta expecificada já em uso, por favor informe outra.')
    exit(1)

sock.sendto(b'Hello', dest)
thread = threading.Thread(target=check_input, args=())
thread.start()

while True:
    data = utils.receiv(sock)
    seq_number = data[0]
    msg = data[1]
    
    if seq_number > last_seq_number:
        if seq_number != last_seq_number + 1:
            lost_pkg_counter += 1
        music_name = msg.split('|')[0]
        line = msg.split('|')[1]
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

    if close_client_flag:
        message = b'bye'
        print('Sending bye message...')
        sock.sendto(message, dest)
        sock.close()
        break   

print("Closing connection to the server...")
print('Total Out of Order Packets received: {}'.format(outOrderPkg))
print('Total lost packages count: {}'.format(lost_pkg_counter))
exit(0)