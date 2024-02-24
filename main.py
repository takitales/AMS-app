from gui import PhoneApp
from wificonnection import WiFiCommunicator

def main():
    communicator = WiFiCommunicator(max_buffer_sz = 128)
    gui = PhoneApp(communicator = communicator)
    gui.mainloop()

if __name__ == "__main__":
    app = PhoneApp()
    app.run()