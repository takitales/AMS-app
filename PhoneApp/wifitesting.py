import socket

ESP_PORT = 1234  # Choose a port number

class wificommands():
    @staticmethod
    def send_command(ip_address, command):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip_address, ESP_PORT))
            s.sendall(command.encode())
            data = s.recv(1024)
