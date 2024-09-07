import kivy
import asyncio
import threading
import random
import jnius

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

# Initialize Pyjnius to use Android's Bluetooth API
BluetoothAdapter = jnius.autoclass('android.bluetooth.BluetoothAdapter')
BluetoothDevice = jnius.autoclass('android.bluetooth.BluetoothDevice')
UUID = jnius.autoclass('java.util.UUID')
BluetoothSocket = jnius.autoclass('android.bluetooth.BluetoothSocket')

# Bluetooth variable
ble_socket = None

# Detects buttons being held
class PushHoldButton(Button):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
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
            setattr(App.get_running_app(), flag_name, 0)

            # Update the label text
            layout = App.get_running_app().root
            layout.children[0].text = "No Button Pressed!"
            App.get_running_app().send_command('s')  # Send stop command

            return True
        return super().on_touch_up(touch)

    def check_hold(self, dt):
        self.dispatch('on_hold')

    def on_hold(self, *args):
        match self.text:
            case "Up":
                App.get_running_app().send_command('u')
            case "Right":
                App.get_running_app().send_command('r')
            case "Left":
                App.get_running_app().send_command('l')
            case "Down":
                App.get_running_app().send_command('d')
            case "Manual":
                App.get_running_app().send_command('m')


class PhoneApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_textinput = None
        self.adapter = BluetoothAdapter.getDefaultAdapter()

    def connect_bluetooth(self, address):
        global ble_socket
        device = self.adapter.getRemoteDevice(address)
        uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")  # Bluetooth serial UUID
        ble_socket = device.createRfcommSocketToServiceRecord(uuid)

        try:
            ble_socket.connect()
            print(f"Connected to Bluetooth device: {address}")
        except Exception as e:
            print(f"Failed to connect: {e}")
            ble_socket = None
    
    def on_connect_button_pressed(self, instance):
        if self.ip_textinput:
            ble_address = self.ip_textinput.text
            threading.Thread(target=self.connect_bluetooth, args=(ble_address,)).start()
    
    def send_command(self, command):
        global ble_socket
        if ble_socket:
            try:
                ble_socket.getOutputStream().write(command.encode())
                print(f"Sent command: {command}")
            except Exception as e:
                print(f"Bluetooth Error: {e}")

    def holdButton(self, instance):
        flag_name = instance.text.lower() + "Flag"
        flag_value = 1 if instance.is_holding else 0
        setattr(self, flag_name, flag_value)

        # Get the instances of buttons from the layout
        layout = self.root
        upbtn = layout.children[1]
        downbtn = layout.children[2]
        leftbtn = layout.children[3]
        rightbtn = layout.children[4]

        # Check if any button is being held down
        if not any(btn.is_holding for btn in [upbtn, downbtn, leftbtn, rightbtn]):
            self.root.children[0].text = "No Button Pressed!"
            self.send_command('s')  # send stop command
        else:
            pressed_buttons = [btn.text for btn in [upbtn, downbtn, leftbtn, rightbtn] if btn.is_holding]
            self.root.children[0].text = f"{', '.join(pressed_buttons)} Button(s) Pressed!"
            commands = {"Up": 'u', "Right": 'r', "Left": 'l', "Down": 'd', "Manual": 'm'}
            for btn in [upbtn, downbtn, leftbtn, rightbtn]:
                if btn.is_holding:
                    self.send_command(commands[btn.text])

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

        # Add buttons and functionality for controls
        manbtn = PushHoldButton(text="Manual", size_hint=(.1, .1), pos_hint={'center_x': .1, 'center_y': .1}, background_color=[1, 1, 1, 1])
        layout.add_widget(manbtn)
        manbtn.bind(on_hold=self.holdButton)

        upbtn = PushHoldButton(text="Up", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .4}, background_color=[1, 1, 1, 1])
        layout.add_widget(upbtn)
        upbtn.bind(on_hold=self.holdButton)

        downbtn = PushHoldButton(text="Down", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .1}, background_color=[1, 1, 1, 1])
        layout.add_widget(downbtn)
        downbtn.bind(on_hold=self.holdButton)

        leftbtn = PushHoldButton(text="Left", size_hint=(.1, .1), pos_hint={'center_x': .7, 'center_y': .25}, background_color=[1, 1, 1, 1])
        layout.add_widget(leftbtn)
        leftbtn.bind(on_hold=self.holdButton)

        rightbtn = PushHoldButton(text="Right", size_hint=(.1, .1), pos_hint={'center_x': .9, 'center_y': .25}, background_color=[1, 1, 1, 1])
        layout.add_widget(rightbtn)
        rightbtn.bind(on_hold=self.holdButton)

        # Label for button feedback
        label = Label(text=" ", size_hint=(.5, .5), pos_hint={'center_x': .5, 'center_y': .9})
        layout.add_widget(label)

        return layout
