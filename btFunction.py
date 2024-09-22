import asyncio
from jnius import autoclass
# from bleak import BleakClient (works with windows)

deviceAddress = "B0:B2:1C:51:E6:A6"
#"E8:31:CD:C4:DE:7E"  robot esp32
#"B0:B2:1C:51:E6:A6" my esp32
characteristicUUID = "0eea86fb-1900-4348-9d86-d4ad7412df58"

# Get access to Java classes
BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = autoclass('android.bluetooth.BluetoothDevice')
BluetoothSocket = autoclass('android.bluetooth.BluetoothSocket')
UUID = autoclass('java.util.UUID')

# Context and activity to interact with the Android environment
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Context = PythonActivity.mActivity

# checks if bluetooth is enabled and if not request
def enable_bluetooth():
    bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()

    if bluetooth_adapter is None:
        print("Device does not support Bluetooth")
        return False

    if not bluetooth_adapter.isEnabled():
        # Request to enable Bluetooth
        Intent = autoclass('android.content.Intent')
        BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
        activity = PythonActivity.mActivity
        enable_bt_intent = Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE)
        activity.startActivityForResult(enable_bt_intent, 1)

    return bluetooth_adapter.isEnabled()

# discover nearby bluetooth devices
def discover_devices():
    bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()
    if not bluetooth_adapter.isEnabled():
        print("Bluetooth is not enabled!")
        return

    # Start device discovery
    bluetooth_adapter.startDiscovery()
    
    receiver = autoclass('android.content.BroadcastReceiver')
    
    class BluetoothReceiver(receiver):
        def onReceive(self, context, intent):
            action = intent.getAction()
            if action == BluetoothDevice.ACTION_FOUND:
                device = intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
                device_name = device.getName()
                device_address = device.getAddress()
                print(f"Found device: {device_name} ({device_address})")
    
    # Register the receiver
    IntentFilter = autoclass('android.content.IntentFilter')
    filter = IntentFilter(BluetoothDevice.ACTION_FOUND)
    Context.registerReceiver(BluetoothReceiver(), filter)

#connect to bluetooth device
def connect_to_device(device_address):
    bluetooth_adapter = BluetoothAdapter.getDefaultAdapter()

    if not bluetooth_adapter.isEnabled():
        print("Bluetooth is not enabled!")
        return

    device = bluetooth_adapter.getRemoteDevice(device_address)
    uuid = UUID.fromString(characteristicUUID)  # Standard UUID for serial communication

    # Create Bluetooth socket
    bluetooth_socket = device.createRfcommSocketToServiceRecord(uuid)
    
    try:
        bluetooth_socket.connect()
        print(f"Connected to {device_address}")
    except Exception as e:
        print(f"Could not connect to {device_address}: {e}")
    
    return bluetooth_socket

def send_data(bluetooth_socket, data):
    try:
        output_stream = bluetooth_socket.getOutputStream()
        output_stream.write(data.encode())
        output_stream.flush()
        print(f"Sent data: {data}")
    except Exception as e:
        print(f"Failed to send data: {e}")


# async def connectBLE(address):
    # global client 
    # client = BleakClient(address)
    # try:
    # await client.connect()
        # if client.is_connected:
            #print("Client is connected")
        # else:
            #print("Client is not connected")
    # except Exception as e:
        # print(f"An error ocurred in connection: {e}")    

# async def sendSerialData(data):
    # try:
                    #write data to the characteristic
    # await client.write_gatt_char(characteristicUUID,data.encode())
                    # print("Data sent Successfully")
    # except Exception as e:
        # print(f"An error ocurred: {e}")
        
        
#btsocket = connect_to_device(deviceAddress)
# asyncio.run(connectBLE(deviceAddress))
# asyncio.run(sendSerialData("u"))
# asyncio.run(sendSerialData("d"))
# asyncio.run(sendSerialData("l"))
# asyncio.run(sendSerialData("r"))
# asyncio.run(sendSerialData("r"))
# asyncio.run(sendSerialData("l"))