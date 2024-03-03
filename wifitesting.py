import socket
import time

ESP_IP = '192.168.1.12'  # Replace with the IP address of your ESP32
ESP_PORT = 1234  # Choose a port number

class wificommands():
        guiCommand = ''
        def send_command(command):
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((ESP_IP, ESP_PORT))
                        s.sendall(command.encode())
                        data = s.recv(1024)
                        print('Received', repr(data))
                        
        # Connect to ESP32 and send commands
        if True:
                #print("Command Received: " + guiCommand)
                command_config  = guiCommand #= input("Enter command (on/off): ")
                print("Command Received: " + command_config)
                if command_config.lower() == 'up':
                        command_config = 'u'
                elif command_config.lower() == 'down':
                        command_config = 'd'
                elif command_config.lower() == 'left':
                        command_config = 'l'
                elif command_config.lower() == 'right':
                        command_config = 'r'

                send_command(command_config)
                #time.sleep(1)
