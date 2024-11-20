import kivy
import time
import threading
import random
import asyncio
import webbrowser

# from bleak import BleakClient
from btFunction import sendSerialData
from btFunction import connectBLE
from bleak import BleakClient #import BleakClient

#kivy imports
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
from concurrent.futures import ThreadPoolExecutor
from kivy.lang import Builder


global buttonFlag

deviceAddress = "AC:0B:FB:5C:C9:02"
#"E8:31:CD:C4:DE:7E"  robot esp32
#"B0:B2:1C:51:E6:A6" my esp32
#"B0:B2:1C:51:E5:EA" beacon esp32
#"AC:0B:FB:5C:C9:02" esp32 pico address


#create colors for button
grey = [1,1,1,1]


#handles the demo buttons to be a toggle to be pressed ones
class toggleButton(Button):
    # Initializations
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.register_event_type('on_hold')
        self.is_toggled = False
        self.hold_trigger = None
        self.is_holding = False
    
    # Handling touch down
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            self.is_toggled = not self.is_toggled  # Toggle state
            if self.is_toggled:
                self.is_holding = True
                self.hold_trigger = Clock.schedule_interval(self.check_hold, 0.1)
            else:
                self.reset_state()
            return True
        return super().on_touch_down(touch)

     # Handling touch up
    def on_touch_up(self, touch):
        if self.hold_trigger and not self.is_toggled:
            self.reset_state()
            return True
        return super().on_touch_up(touch)
    
   # Resetting the button state
    def reset_state(self):
        self.is_holding = False
        if self.hold_trigger:
            self.hold_trigger.cancel()
            self.hold_trigger = None

        # Reset the flag for the button
        flag_name = self.text.lower() + "Flag"
        setattr(App.get_running_app(), flag_name, 0)

        # Update label to show no button is pressed
        layout = App.get_running_app().root
        layout.children[0].text = "No Button Pressed!"
    
    
    # Checking hold status
    def check_hold(self, dt):
        if self.is_toggled and self.is_holding:
            self.dispatch('on_hold')
        else:
            self.reset_state()
            
    # Handling the hold action
    def on_hold(self, *args):
        match self.text:
            case "Demo_1":
                if buttonFlag == 0:
                    asyncio.run(sendSerialData("m")) #sends 'm' to the robot to be handled
                    print("m")
                    buttonFlag = 1
                else:
                    buttonFlag = 0
                
            case "Demo_2":
                if buttonFlag == 0:
                    asyncio.run(sendSerialData("n"))
                    print("n")
                    buttonFlag = 1
                else:
                    buttonFlag = 0
    
        
        
        

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
                asyncio.run(sendSerialData("u")) #sends 'u' through the server to be handled by the robot
            case "Right":
                asyncio.run(sendSerialData("r"))
            case "Left":
                asyncio.run(sendSerialData("l"))
            case "Down":
                asyncio.run(sendSerialData("d"))
            case "Demo_1":
                asyncio.run(sendSerialData("m"))
                print("m")
            case "Demo_2":
                asyncio.run(sendSerialData("n"))
                print("n")
            case "Live Feed":
                print("L")
                openHyperlink()
                
                
                
#function for opening links and having a button open a link
def openHyperlink():
    webbrowser.open('http://www.google.com')
    print("opening link....")


#create class for button
class PhoneApp(App):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_textinput = None
        self.client = None #initialize BleakClient
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.executor = ThreadPoolExecutor() #use a threadpoolexecutor
    
    async def connect_to_device(self):
        async with BleakClient(deviceAddress) as client:
            self.client = client
            await client.start_notify(
                "0eea86fb-1900-4348-9d86-d4ad7412df58", #CHARACTERISTIC_UUID
                self.notifcation_handler
            )
            
    def update_label(self, message):
        self.root.children[0].text = f"Received: {message}"
        
    def notifcation_handler(self, sender, data):
        message = data.decode('utf-8')  # Decode the notification data
        # Update the label with the received message
        Clock.schedule_once(lambda dt: self.update_label(message))
        
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
        manbtn = layout.children[5]
        cntbtn = layout.children[6]
        cameraButton = layout.children[7]

        # Check if any button is being held down
        if not any(btn.is_holding for btn in [upbtn, downbtn, leftbtn, rightbtn, manbtn, cntbtn, cameraButton]):
            self.root.children[0].text = "No Button Pressed!"
        else:
            pressed_buttons = [btn.text for btn in [upbtn, downbtn, leftbtn, rightbtn, manbtn, cntbtn, cameraButton] if btn.is_holding]
            self.root.children[0].text = f"{', '.join(pressed_buttons)} Button(s) Pressed!"
    
    async def async_on_start(self):
        await self.connect_to_device()
        
    def start_async_tasks(self):
        self.loop.run_in_executor(self.executor, lambda: asyncio.run(self.async_on_start()))
    
    
    # Create Buttons and Press Functionality
    def build(self):
        layout = FloatLayout()
        
        #initial connection
        Clock.schedule_once(lambda dt: asyncio.ensure_future(self.async_on_start()))
        
        # hyperlink button
        cameraButton = PushHoldButton(text = "Lidar Data", size_hint=(.1,.1), pos_hint={'center_x':.5,'center_y':.1}, background_color = grey)
        layout.add_widget(cameraButton)
        cameraButton.bind(on_hold=self.holdButton)
        
        # Demo 2 button
        cntbtn = PushHoldButton(text = "Demo_2", size_hint=(.1,.1), pos_hint={'center_x':.3,'center_y':.1}, background_color = grey)
        layout.add_widget(cntbtn)
        cntbtn.bind(on_hold=self.holdButton)
        
        
        # Demo 1 button to showcase the robot moves with the app
        manbtn = PushHoldButton(text = "Demo_1", size_hint=(.1,.1), pos_hint={'center_x':.1,'center_y':.1}, background_color = grey)
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
    
    def on_stop(self):
        self.executor.shutdown(wait=False)
