import kivy
import time
import threading
import random
import asyncio 
from bleak import BleakScanner, BleakClient

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.textinput import TextInput


#create colors for button
grey = [1,1,1,1]

async def read_characteristic(client,char_uuid):
    value = await client.read_gatt_char(char_uuid)
    print(f"characteristic value: {value}")

async def write_characteristic(client, char_uuid, value):
    await client.write_gatt_char(char_uuid, value)
    print("Write Successful")
  
# detects buttons being held
class PushHoldButton(Button):
    
    # creating initializations
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_hold')
        self.hold_trigger = None
        self.is_holding = False
        
    # checking if button is pressed
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_holding = True
            self.hold_trigger = Clock.schedule_interval(self.check_hold, 0.1)
            return True
        return super().on_touch_down(touch)
    
    # checking if button is released
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

            return True
        return super().on_touch_up(touch)

    # checks if button is being held
    def check_hold(self, dt):
        self.dispatch('on_hold')

    # checks which button is pressed and sends command over to esp to deal with character press
    def on_hold(self, *args):
        match self.text:
            case "Up":
                print("idk")
            case "Right":
                print("pizza")
            case "Left":
                print("ahhh")
            case "Down":
                print("something")
            case "Manual":
                print("hi")



#create class for button
class PhoneApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_textinput = None
    
    #change to bluetooth unless i can figure out how to automatically connect to bluetooth
    def on_connect_button_pressed(self, instance):
        global ESP_IP
        if self.ip_textinput:
            ip_address = self.ip_textinput.text
            
            print("Connecting to:", ip_address)
            ESP_IP = ip_address  # Update the ESP32 IP address
    
    # Handle actions when button is held down
    def holdButton(self, instance):
        flag_name = instance.text.lower() + "Flag"
        flag_value = 1 if instance.is_holding else 0
        print(flag_value)
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
        else:
            pressed_buttons = [btn.text for btn in [upbtn, downbtn, leftbtn, rightbtn] if btn.is_holding]
            self.root.children[0].text = f"{', '.join(pressed_buttons)} Button(s) Pressed!"

    # Create Buttons and Press Functionality
    def build(self):
        layout = FloatLayout()
        
        #text input
        self.ip_textinput = TextInput(
            hint_text = "Enter Ip Address",
            size_hint=(.4, None),
            pos_hint={'center_x': .5, 'center_y': .6},
            multiline = False
        )
        layout.add_widget(self.ip_textinput)
        
        #connect button
        connect_button = Button(
            text="Connect",
            size_hint=(.2, None),
            pos_hint={'center_x': .5, 'center_y': .4},
            on_press=self.on_connect_button_pressed
        )
        layout.add_widget(connect_button)
        
        # add manual mode to take over robot
        manbtn = PushHoldButton(text = "Manual", size_hint=(.1,.1), pos_hint={'center_x':.1,'center_y':.1}, background_color = grey)
        layout.add_widget(manbtn)
        manbtn.bind(on_hold=self.holdButton)
        
        # add up button
        upbtn = PushHoldButton(text="Up", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .4}, background_color=grey)
        layout.add_widget(upbtn)
        upbtn.bind(on_hold=self.holdButton)

        # add down button
        downbtn = PushHoldButton(text="Down", size_hint=(.1, .1), pos_hint={'center_x': .8, 'center_y': .1}, background_color=grey)
        layout.add_widget(downbtn)
        downbtn.bind(on_hold=self.holdButton)

        # left button
        leftbtn = PushHoldButton(text="Left", size_hint=(.1, .1), pos_hint={'center_x': .7, 'center_y': .25}, background_color=grey)
        layout.add_widget(leftbtn)
        leftbtn.bind(on_hold=self.holdButton)

        # right button
        rightbtn = PushHoldButton(text="Right", size_hint=(.1, .1), pos_hint={'center_x': .9, 'center_y': .25}, background_color=grey)
        layout.add_widget(rightbtn)
        rightbtn.bind(on_hold=self.holdButton)
        
        # label showing which button was pressed
        label = Label(text=" ", size_hint=(.5, .5), pos_hint={'center_x': .5, 'center_y': .9})
        layout.add_widget(label)

        return layout
