import socket
import time

ESP_IP = '192.168.1.12'  # Replace with the IP address of your ESP32
ESP_PORT = 1234  # Choose a port number

class wificommands():
        def send_command(command):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ESP_IP, ESP_PORT))
                        s.sendall(command.encode())
                        data = s.recv(1024)
