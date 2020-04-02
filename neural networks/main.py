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
from kivy.uix.scrollview import ScrollView


from kivymd.app import MDApp
from kivymd.uix.bottomnavigation import MDBottomNavigationItem
from kivymd.uix.card import MDCard
from kivymd.uix.snackbar import Snackbar
from kivymd.toast import toast

from kivy.uix.image import Image
from kivy.clock import Clock
from kivy.graphics.texture import Texture

import PIL
import speech_recognition as sr
import cv2


Window.softinput_mode = "below_target"  # resize to accomodate keyboard
Window.keyboard_anim_args = {'d': 0.5, 't': 'in_out_quart'}

Builder.load_string("""
#:import utils kivy.utils
#:include kv/login.kv
#:include kv/home.kv
#:include kv/explore.kv

#:import Snackbar kivymd.uix.snackbar.Snackbar

""")


class ExploreScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.capture = cv2.VideoCapture(0)
        #cv2.namedWindow("CV2 Image",cv2.WINDOW_NORMAL)
        #cv2.resizeWindow("CV2 Image", 380,200)
        Clock.schedule_interval(self.update, 1.0/33.0)

    def update(self, dt):
        self.ids.vid.reload()
        # display image from cam in opencv window
        ret, frame = self.capture.read()
        cv2.imwrite("camera.jpg",frame)

    def speechRec(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            audio = r.listen(source, timeout=1)
            try:
                text = r.recognize_google(audio)
                if(text == "start"):
                    toast("Starting the car!")
                elif(text == "stop" or text == "top"):
                    toast("Stopping the car!")
                else:
                    text("Could not recognize what you said!")
            except:
                toast("Could not recognize what you said!")

    def carControl(self, control):
        if(control == "start"):
            toast("Starting the car!")
        elif(control == "stop"):
            toast("Stopping the car!")

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
