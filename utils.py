import struct 

BUFF_SIZE = 200

def send(sock, dest, data):
  # in order: sequence number, data
  packed = struct.pack('i {}s'.format(BUFF_SIZE), data[0], data[1].encode())
  sock.sendto(packed, dest)

def receiv(sock):
    data, _ = sock.recvfrom(BUFF_SIZE + 4)
    # in order: SEQUENCE NUMBER, DATA
    upk = struct.unpack('i {}s'.format(BUFF_SIZE), data)
    return (upk[0], upk[1].decode("utf-8"))