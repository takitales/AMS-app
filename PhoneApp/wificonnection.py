import socket

HOST = '192.168.1.100'  # IP address of your microcontroller
PORT = 1234             # Port number you're using for communication

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello, microcontroller!')
    data = s.recv(1024)

print('Received', repr(data))
