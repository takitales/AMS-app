import kivy
import random 

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout

#create colors for button
grey = [1,1,1,1]

#create class for button
class PhoneApp(App):
    def build(self):
        
        #add up button
        layout = FloatLayout()
        upbtn = Button(text = "Up",size_hint = (.1,.1),pos_hint = {'center_x': .8, 'center_y':.4},background_color = grey)
        layout.add_widget(upbtn)
        upbtn.bind(on_press=self.pressButton)
        
        #add down button
        downbtn = Button(text = "Down",size_hint = (.1,.1),pos_hint = {'center_x': .8, 'center_y':.1},background_color = grey)
        layout.add_widget(downbtn)
        downbtn.bind(on_press=self.pressButton)
        
        #right button
        rightbtn = Button(text = "Right",size_hint = (.1,.1),pos_hint = {'center_x': .7, 'center_y':.25},background_color = grey)
        layout.add_widget(rightbtn)
        rightbtn.bind(on_press=self.pressButton)
        
        
        #left button
        lftbtn = Button(text = "Left",size_hint = (.1,.1),pos_hint = {'center_x': .9, 'center_y':.25},background_color = grey)
        layout.add_widget(lftbtn)
        lftbtn.bind(on_press=self.pressButton)
        
        
        return layout
    
    def pressButton(self, instance):
        if instance.text == "Up":
            print("Up Button Pressed!")
        elif instance.text == "Down":
            print("Down Button Pressed!")
        elif instance.text == "Right":
            print("Right Button Pressed!")
        elif instance.text == "Left":
            print("Left Button Pressed!")
        else:
            print("Unknown Button Pressed")
        
if __name__ == "__main__":
    app = PhoneApp()
    app.run()