import asyncio
from bleak import BleakClient

deviceAddress = "B0:B2:1C:51:E6:A6"
#"E8:31:CD:C4:DE:7E"  robot esp32
#"B0:B2:1C:51:E6:A6" my esp32
characteristicUUID = "0eea86fb-1900-4348-9d86-d4ad7412df58"

async def connectBLE(address):
    global client 
    client = BleakClient(address)
    # try:
    await client.connect()
        # if client.is_connected:
            #print("Client is connected")
        # else:
            #print("Client is not connected")
    # except Exception as e:
        # print(f"An error ocurred in connection: {e}")    

async def sendSerialData(data):
    # try:
                    #write data to the characteristic
    await client.write_gatt_char(characteristicUUID,data.encode())
                    # print("Data sent Successfully")
    # except Exception as e:
        # print(f"An error ocurred: {e}")
# asyncio.run(connectBLE(deviceAddress))
# asyncio.run(sendSerialData("u"))
# asyncio.run(sendSerialData("d"))
# asyncio.run(sendSerialData("l"))
# asyncio.run(sendSerialData("r"))
# asyncio.run(sendSerialData("r"))
# asyncio.run(sendSerialData("l"))