#kivy-latest
#kivymd- 0.103.0

import traceback

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.factory import Factory
from kivy.animation import Animation
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivymd.uix.behaviors import CircularRippleBehavior
from kivymd.toast.kivytoast.kivytoast import toast
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty

from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import Snackbar
from kivymd.toast import toast

import cv2
import numpy as np
import socket

Window.softinput_mode = "below_target"  # resize to accomodate keyboard
Window.keyboard_anim_args = {'d': 0.5, 't': 'in_out_quart'}

Builder.load_string("""
#:import utils kivy.utils
#:include kv/login.kv
#:include kv/home.kv
#:include kv/explore.kv
""")


class ExploreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_socket = socket.socket()
        self.server_socket.bind(("192.168.0.100", 1235))
        self.server_socket.listen(0)

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')
        
    def drive(self):
        stream_bytes = b' '
        try:
            # stream video frames one by one
            while True:  
                #self.ids.vid.reload()   
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                    Clock.schedule_interval(self.update, 1.0/33.0)

        finally:
            self.connection.close()
            self.server_socket.close()

    def update(self, dt):
        self.ids.vid.reload()
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        cv2.imwrite("camera.jpg",frame)

class Car(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Infernus"
        self.theme_cls.primary_palette = "DeepOrange"
        self.theme_cls.theme_style = "Light"
        self.sm = ScreenManager()
        self.has_animated_card = False
        self.has_animated_background = False
        
    def login(self, usr, passwd):
        if(usr.text=="salman97" and passwd.text=="salman"):
            #Snackbar(text="Welcome " + usr.text + "!").show()
            toast("Welcome " + usr.text + "!")
            self.manage_screens("home_screen", "add")
            self.change_screen("home_screen")

        else:
            toast("Incorrect username and/or password!")
            #Snackbar(text="Incorrect username and/or password!").show()

    def animate_background(self, widget):
        if self.has_animated_background == False:
            anim = Animation(size_hint_y=1) + Animation(size_hint_y=0.5)
            anim.start(widget.ids.bx)
        
    def animate_card(self, widget):
        # {"center_x": 0.5, "center_y": 0.6}
        if self.has_animated_card == False:
            anim = Animation(pos_hint={"center_x": 0.5, "center_y": 0.6}, duration=0.5)
            anim.start(widget)
            self.has_animated_card = True
           
    def change_screen(self, screen_name):
        if self.sm.has_screen(screen_name):
            self.sm.current = screen_name
        

    def manage_screens(self, screen_name, action):
        scns = {
            "login_screen": Factory.LoginScreen,
            "home_screen": Factory.HomeScreen,
            "explore_screen": Factory.ExploreScreen
        }
        try:

            if action == "remove":
                if self.sm.has_screen(screen_name):
                    self.sm.remove_widget(self.sm.get_screen(screen_name))
                #print("Screen ["+screen_name+"] removed")
            elif action == "add":
                if self.sm.has_screen(screen_name):
                    pass
                    #print("Screen [" + screen_name + "] already exists")
                else:
                    self.sm.add_widget(scns[screen_name](name=screen_name))
                    #print(screen_name + " added")
                    #print("Screen ["+screen_name+"] added")
        except:
            print(traceback.format_exc())
            print("Traceback ^.^")

    def on_pause(self):
        return True

    def on_resume(self):
        pass

    def build(self):
        #print('hello')
        self.bind(on_start=self.post_build_init)
        self.sm.add_widget(Factory.LoginScreen())
        self.sm.add_widget(Factory.HomeScreen())
        self.sm.current = "login_screen"
        return self.sm

    def post_build_init(self, ev):
        win = self._app_window
        win.bind(on_keyboard=self._key_handler)

    def _key_handler(self, *args):
        key = args[1]
        # 1000 is "back" on Android
        # 27 is "escape" on computers
        if key in (1000, 27):
            try:
                self.sm.current = "login_screen"
            except Exception as e:
                print(e)
            return True
        elif key == 1001:
            try:
                self.sm.current = "login_screen"
            except Exception as e:
                print(e)
            return True

if __name__ == "__main__":
    car = Car()
    car.run()
