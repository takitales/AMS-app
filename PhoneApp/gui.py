import kivy
import time
import threading
import PhoneApp.wifitesting as wifitesting
import random

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
ESP_IP = '192.168.1.69'
#class for gps box
class GPSBox(Widget):
    def __init__(self,**kwargs):
        super(GPSBox, self).__init__(**kwargs)
        with self.canvas:
            Color(1,0,0) #color red
            self.dot = Ellipse(pos=(100,100), size=(10,10)) #creates dot for tracking
            self.line = Line(points=[],width=2)
        self.prev_dot_pos = (100, 100)  # Initialize previous dot position
        
        
    def update_dot_position(self,latitude,longitude):
        #convert gps coordinates to position in the box
        box_width, box_height = self.size
        x = (longitude/360.0) * box_width
        y = (latitude/360.0) * box_height
        new_pos = (self.center_x + x - 5, self.center_y + y - 5) #adjusts offset for smaller box

        #Draw line between previous and new positions
        with self.canvas:
            Color(1, 0, 0)  #Set line color
            Line(points=[self.prev_dot_pos[0] + 5, self.prev_dot_pos[1] + 5, new_pos[0] + 5, new_pos[1] + 5], width=2)
        
        self.dot.pos = new_pos  #Update dot position
        self.prev_dot_pos = new_pos  #Update previous dot position
        
        Clock.schedule_once(self.clear_line, 1.0)
    
    def clear_line(self, dt):
        self.line = Line(points=[],width=2)


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
            
            #send stop command
            wifitesting.wificommands.send_command(ESP_IP,'s')

            return True
        return super().on_touch_up(touch)

    def check_hold(self, dt):
        self.dispatch('on_hold')

    def on_hold(self, *args):
        match self.text:
            case "Up":
                wifitesting.wificommands.send_command(ESP_IP,'u')
            case "Right":
                wifitesting.wificommands.send_command(ESP_IP,'r')
            case "Left":
                wifitesting.wificommands.send_command(ESP_IP,'l')
            case "Down":
                wifitesting.wificommands.send_command(ESP_IP,'d')



#create class for button
class PhoneApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ip_textinput = None
    
    def on_connect_button_pressed(self, instance):
        global ESP_IP
        if self.ip_textinput:
            ip_address = self.ip_textinput.text
            # You can perform connection logic here using the entered IP address
            print("Connecting to:", ip_address)
            ESP_IP = ip_address  # Update the ESP32 IP address
            # You may want to add error handling here
    
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
            size_hint=(.5, None),
            pos_hint={'center_x': .5, 'center_y': .6},
            multiline = False
        )
        layout.add_widget(self.ip_textinput)
        
        #connect button
        connect_button = Button(
            text="Connect",
            size_hint=(.2, None),
            pos_hint={'center_x': .5, 'center_y': .5},
            on_press=self.on_connect_button_pressed
        )
        layout.add_widget(connect_button)
        
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
        label = Label(text="No Button Pressed!", size_hint=(.5, .5), pos_hint={'center_x': .5, 'center_y': .9})
        layout.add_widget(label)

        return layout
