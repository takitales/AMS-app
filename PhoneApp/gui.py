import kivy
import asyncio
import threading
from bleak import BleakClient, BleakError, BleakScanner
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

# Create colors for button
grey = [1, 1, 1, 1]

# Detects buttons being held
class PushHoldButton(Button):
    def __init__(self, app_instance, **kwargs):
        super().__init__(**kwargs)
        self.app_instance = app_instance  # Store the reference in PhoneApp
        self.register_event_type('on_hold')
        self.hold_trigger = None
        self.is_holding = False

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_holding = True
            self.hold_trigger = Clock.schedule_interval(self.check_hold, 0.1)
            return True
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.hold_trigger:
            self.is_holding = False
            self.hold_trigger.cancel()
            self.hold_trigger = None

            # Set flag value to 0
            flag_name = self.text.lower() + "Flag"
            setattr(self.app_instance, flag_name, 0)

            # Update the label text
            layout = self.app_instance.root
            layout.children[0].text = "No Button Pressed!"

            # Send stop command
            asyncio.ensure_future(self.app_instance.send_command_over_bluetooth('s'))  # Call send_command_over_bluetooth

            return True
        return super().on_touch_up(touch)

    def check_hold(self, dt):
        self.dispatch('on_hold')

    def on_hold(self, *args):
        command = {
            "Up": 'u',
            "Right": 'r',
            "Left": 'l',
            "Down": 'd',
            "Manual": 'm'
        }.get(self.text, '')
        if command:
            asyncio.ensure_future(self.app_instance.send_command_over_bluetooth(command))

class PhoneApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_textinput = None
        self.connected = False
        self.client = None
        self.characteristic_uuid = None

    async def connect_to_ble_device_by_address(self, address):
        """Connects to the BLE device using the provided address."""
        self.client = BleakClient(address)
        try:
            await self.client.connect()
            self.connected = self.client.is_connected
            print(f"Connected to: {address}")

            # Automatically find the first writable characteristic
            services = await self.client.get_services()
            for service in services:
                for char in service.characteristics:
                    if 'write' in char.properties:
                        self.characteristic_uuid = char.uuid
                        print(f"Found writable characteristic: {self.characteristic_uuid}")
                        return  # Stop after finding the first writable characteristic

        except BleakError as e:
            self.connected = False
            print(f"Error connecting to BLE device: {e}")

    async def send_command_over_bluetooth(self, command):
        """Sends a command to the ESP32 via Bluetooth."""
        try:
            if self.connected and self.client.is_connected and self.characteristic_uuid:
                await self.client.write_gatt_char(self.characteristic_uuid, command.encode())
                print(f"Sent: {command}")
            else:
                print("Device not connected or characteristic not found.")
        except Exception as e:
            print(f"Error: {e}")

    def on_connect_button_pressed(self, instance):
        """Called when the connect button is pressed."""
        ble_address = self.ip_textinput.text
        if ble_address:
            threading.Thread(target=self.run_ble_scan, args=(ble_address,)).start()  # Pass the address to the scan function

    def run_ble_scan(self, address):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_to_ble_device_by_address(address))
        if self.connected:
            self.root.children[0].text = "Connected"
        else:
            self.root.children[0].text = "Failed to Connect"

    def holdButton(self, instance):
        flag_name = instance.text.lower() + "Flag"
        flag_value = 1 if instance.is_holding else 0
        print(flag_value)
        setattr(self, flag_name, flag_value)

        # Get the instances of buttons from the layout
        layout = self.root
        buttons = {btn.text: btn for btn in layout.children[1:]}
        upbtn = buttons.get("Up")
        downbtn = buttons.get("Down")
        leftbtn = buttons.get("Left")
        rightbtn = buttons.get("Right")

        # Check if any button is being held down
        if not any(btn.is_holding for btn in [upbtn, downbtn, leftbtn, rightbtn] if btn):
            self.root.children[0].text = "No Button Pressed!"
        else:
            pressed_buttons = [btn.text for btn in [upbtn, downbtn, leftbtn, rightbtn] if btn and btn.is_holding]
            self.root.children[0].text = f"{', '.join(pressed_buttons)} Button(s) Pressed!"

    def build(self):
        layout = FloatLayout()

        # Text input
        self.ip_textinput = TextInput(
            hint_text="Enter BLE Address",
            size_hint=(.4, None),
            pos_hint={'center_x': .5, 'center_y': .6},
            multiline=False
        )
        layout.add_widget(self.ip_textinput)

        # Connect button
        connect_button = Button(
            text="Connect",
            size_hint=(.2, None),
            pos_hint={'center_x': .5, 'center_y': .4},
            on_press=self.on_connect_button_pressed
        )
        layout.add_widget(connect_button)

        # Add manual mode to take over robot
        manbtn = PushHoldButton(self, text="Manual", size_hint=(.1, .1), pos_hint={'center_x': .1, 'center_y': .1}, background_color=grey)
        layout.add_widget(manbtn)
        manbtn.bind(on_hold=self.holdButton)

        # Add up button
        upbtn = PushHoldButton(self, text="Up", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .4}, background_color=grey)
        layout.add_widget(upbtn)
        upbtn.bind(on_hold=self.holdButton)

        # Add down button
        downbtn = PushHoldButton(self, text="Down", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .1}, background_color=grey)
        layout.add_widget(downbtn)
        downbtn.bind(on_hold=self.holdButton)

        # Left button
        leftbtn = PushHoldButton(self, text="Left", size_hint=(.1, .1), pos_hint={'center_x': .7, 'center_y': .25}, background_color=grey)
        layout.add_widget(leftbtn)
        leftbtn.bind(on_hold=self.holdButton)

        # Right button
        rightbtn = PushHoldButton(self, text="Right", size_hint=(.1, .1), pos_hint={'center_x': .9, 'center_y': .25}, background_color=grey)
        layout.add_widget(rightbtn)
        rightbtn.bind(on_hold=self.holdButton)

        # Label showing which button was pressed
        label = Label(text=" ", size_hint=(.5, .5), pos_hint={'center_x': .5, 'center_y': .9})
        layout.add_widget(label)

        return layout
