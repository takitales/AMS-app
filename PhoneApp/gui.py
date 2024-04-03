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


#create colors for button
grey = [1,1,1,1]
upFlag = 0
rightFlag = 0
leftFlag = 0
downFlag = 0

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
        

#create class for button
class PhoneApp(App):
    
    #Create Buttons and Press Functionality
    def build(self):
        layout = FloatLayout()
        #gps box
        gps_box = GPSBox(size_hint = (None,None), size=(200,200), pos=(0,0))
        layout.add_widget(gps_box)
        
        #simulate gps data update
        def update_gps(dt):
            
            #simulate getting gps coordinates from gps module
            latitude = random.uniform(-90,90)
            longitude = random.uniform(-180,180)
            
            #update dot position
            gps_box.update_dot_position(latitude,longitude)
        
        #update gps data
        Clock.schedule_interval(update_gps, 1.0)
        
        #add up button
        upbtn = Button(text = "Up",size_hint = (.1,.1),pos_hint = {'center_x': .8, 'center_y':.4},background_color = grey)
        layout.add_widget(upbtn)
        upbtn.bind(on_press=self.pressButton)
        
        #add down button
        downbtn = Button(text = "Down",size_hint = (.1,.1),pos_hint = {'center_x': .8, 'center_y':.1},background_color = grey)
        layout.add_widget(downbtn)
        downbtn.bind(on_press=self.pressButton)
        
        #left button
        leftbtn = Button(text = "Left",size_hint = (.1,.1),pos_hint = {'center_x': .7, 'center_y':.25},background_color = grey)
        layout.add_widget(leftbtn)
        leftbtn.bind(on_press=self.pressButton)
        
        
        #right button
        rightbtn = Button(text = "Right",size_hint = (.1,.1),pos_hint = {'center_x': .9, 'center_y':.25},background_color = grey)
        layout.add_widget(rightbtn)
        rightbtn.bind(on_press=self.pressButton)
        
        #label showing which button was pressed
        label = Label(text = "No Button Pressed!",size_hint = (.5,.5),pos_hint = {'center_x':.5,'center_y':.5})
        layout.add_widget(label)
        
        return layout
    
    #shows text of which button was pressed and handle accordingly
    def pressButton(self, instance):
        global upFlag
        global rightFlag
        global leftFlag
        global downFlag
        if instance.text == "Up":
            if upFlag == 0:
                self.root.children[0].text = "Up Button Pressed! Flag set to 1. Moving up."
                sendThis = 'u'
                wifitesting.wificommands.send_command(sendThis)
                upFlag = 1
            else:
                self.root.children[0].text = "Up Button Pressed! Flag set to 0. Not Moving up."
                sendThis = 'u'
                wifitesting.wificommands.send_command(sendThis)
                upFlag = 0
        elif instance.text == "Down":
            if downFlag == 0:
                self.root.children[0].text = "Down Button Pressed! Flag set to 1. Moving down."
                sendThis = 'd'
                wifitesting.wificommands.send_command(sendThis)
                downFlag = 1
            else:
                self.root.children[0].text = "Down Button Pressed! Flag set to 0. Not Moving down."
                sendThis = 'd'
                wifitesting.wificommands.send_command(sendThis)
                downFlag = 0
        elif instance.text == "Right":
            if rightFlag == 0:
                self.root.children[0].text = "Right Button Pressed! Flag set to 1. Moving right."
                sendThis = 'r'
                wifitesting.wificommands.send_command(sendThis)
                rightFlag = 1
            else:
                self.root.children[0].text = "Right Button Pressed! Flag set to 0. Not Moving right."
                sendThis = 'r'
                wifitesting.wificommands.send_command(sendThis)
                rightFlag = 0
        elif instance.text == "Left":
            if leftFlag == 0:
                self.root.children[0].text = "Left Button Pressed! Flag set to 1. Moving left."
                sendThis = 'l'
                wifitesting.wificommands.send_command(sendThis)
                leftFlag = 1
            else:
                self.root.children[0].text = "Left Button Pressed! Flag set to 0. Not Moving left."
                sendThis = 'l'
                wifitesting.wificommands.send_command(sendThis)
                leftFlag = 0
        else:
            print("Unknown Button Pressed")
            self.root.children[0].text = "Unkown Button Pressed!"
    
            
    print('Button Events Created Successfully!') #shows in terminal if button events were created