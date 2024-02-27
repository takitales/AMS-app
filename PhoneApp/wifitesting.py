import socket
import time

ESP_IP = '192.168.1.12'  # Replace with the IP address of your ESP32
ESP_PORT = 1234  # Choose a port number

def send_command(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((ESP_IP, ESP_PORT))
        s.sendall(command.encode())
        data = s.recv(1024)
        print('Received', repr(data))

# Connect to ESP32 and send commands
while True:
    command = input("Enter command (on/off): ")
    if command.lower() == 'on':
            command = 'o'
    else:
            command = 'f'
            
    if command.lower() == 'o' or command.lower() == 'f':
            print("Sending Command")
            send_command(command)
    else:
        print("Invalid command. Please enter 'on' or 'off'.")
    #time.sleep(1)
