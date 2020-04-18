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
        self.server_socket.bind((host, port))
        self.server_socket.listen(0)

        # accept a single connection
        self.connection = self.server_socket.accept()[0].makefile('rb')
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('192.168.0.101', 1234))   #pi
        
        # load trained neural network
        self.nn = NeuralNetwork()
        self.nn.load_modelKeras("model_test.h5")

        self.h1 = 5.5 #stop sign - measure manually
        self.h2 = 5.5 #traffic light

        #self.stop_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +"C:/Users/My\ PC/Anaconda3/envs/tf/Lib/site-packages/cv2/data/stop_sign.xml")
        #self.stop_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +"D:/Downloads/self-driving-car2/neural networks/stop_sign.xml")
        self.stop_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +"stop_sign.xml")
        self.traffic_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "traffic_light.xml")   

        self.d_stop_light_thresh = 70
        self.d_stop_sign = self.d_stop_light_thresh    
        self.d_light = self.d_stop_light_thresh
        
        self.stop_start = 0  # start time when stop at the stop sign
        self.stop_finish = 0
        self.stop_time = 0
        self.drive_time_after_stop = 0

        self.red_light = False
        self.green_light = False
        self.yellow_light = False

        self.alpha = 8.0 * math.pi / 180    # degree measured manually
        self.v0 = 119.865631204             # from camera matrix
        self.ay = 332.262498472             # from camera matrix

    def drive(self):
        stop_flag = False
        stop_sign_active = True
        stream_bytes = b' '
        try:
            # stream video frames one by one
            while True:     
                stream_bytes += self.connection.read(1024)
                first = stream_bytes.find(b'\xff\xd8')
                last = stream_bytes.find(b'\xff\xd9')

                if first != -1 and last != -1:
                    jpg = stream_bytes[first:last + 2]
                    stream_bytes = stream_bytes[last + 2:]
                    gray = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_GRAYSCALE)
                    image = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                    # lower half of the image
                    height, width = gray.shape
                    roi = gray[int(height/2):height, :]
                    #print("Image loaded")
                    
                    #frame= cv2.resize(image, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)

                    # object detection
                    v_param1 = self.detect(self.stop_cascade, gray, image)
                    v_param2 = self.detect(self.traffic_cascade, gray, image)

                    # distance measurement
                    if v_param1 > 0 or v_param2 > 0:
                        d1 = self.calculate(v_param1, self.h1, 300, image)
                        d2 = self.calculate(v_param2, self.h2, 100, image)
                        self.d_stop_sign = d1
                        self.d_light = d2
                    
                    cv2.imshow('RPi Camera Stream', image)
                    cv2.waitKey(1)

                    # reshape image
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
                    
                    if 0 < self.d_stop_sign < self.d_stop_light_thresh and stop_sign_active:
                        print("Stop sign ahead")
                        label = "3"
                        self.sendPrediction(label)
                        #self.rc_car.stop()

                        # stop for 5 seconds
                        if stop_flag is False:
                            self.stop_start = cv2.getTickCount()
                            stop_flag = True
                        self.stop_finish = cv2.getTickCount()

                        self.stop_time = (self.stop_finish - self.stop_start) / cv2.getTickFrequency()
                        print("Stop time: %.2fs" % self.stop_time)

                        # 5 seconds later, continue driving
                        if self.stop_time > 5:
                            print("Waited for 5 seconds")
                            stop_flag = False
                            stop_sign_active = False

                    elif 0 < self.d_light < self.d_stop_light_thresh:
                        # print("Traffic light ahead")
                        if self.red_light:
                            print("Red light")
                            label = "3"
                            self.sendPrediction(label)
                        elif self.green_light:
                            print("Green light")
                            pass
                        elif self.yellow_light:
                            print("Yellow light")
                            pass

                        self.d_light = self.d_stop_light_thresh
                        self.red_light = False
                        self.green_light = False
                        self.yellow_light = False

                    else:
                        stop_sign_active = True

                        # neural network makes prediction                   
                        self.prediction = self.nn.predictKeras(image_array)
                        #print("Keras prediction: ",self.prediction)
                        
                        label = self.prediction[0]
                        label = str(label)
                        self.sendPrediction(label)
                        
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Car stopped")
                        self.sendPrediction("3")
                        break
        finally:
            cv2.destroyAllWindows()
            self.connection.close()
            self.server_socket.close()

    def sendPrediction(self, pred):
        p=pred+ ' '
        p = p.encode('utf-8')
        self.client_socket.send(p)
        #print('Prediction sent to Pi')

    def calculate(self, v, h, x_shift, image):
        # compute and return the distance from the target point to the camera
        d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
        if d > 0:
            cv2.putText(image, "%.1fcm" % d,
                        (image.shape[1] - x_shift, image.shape[0] - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return d

    def detect(self, cascade_classifier, gray_image, image):

        # y camera coordinate of the target point 'P'
        v = 0

        # detection
        cascade_obj = cascade_classifier.detectMultiScale(
            gray_image,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30))

        # draw a rectangle around the objects
        for (x_pos, y_pos, width, height) in cascade_obj:
            cv2.rectangle(image, (x_pos + 5, y_pos + 5), (x_pos + width - 5, y_pos + height - 5), (255, 255, 255), 2)
            v = y_pos + height - 5
            # print(x_pos+5, y_pos+5, x_pos+width-5, y_pos+height-5, width, height)

            # stop sign
            if width / height == 1:
                cv2.putText(image, 'STOP', (x_pos, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            else:
                roi = gray_image[y_pos + 10:y_pos + height - 10, x_pos + 10:x_pos + width - 10]
                mask = cv2.GaussianBlur(roi, (25, 25), 0)
                (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(mask)

                # check if light is on
                if maxVal - minVal > threshold:
                    cv2.circle(roi, maxLoc, 5, (255, 0, 0), 2)

                    # Red light
                    if 1.0 / 8 * (height - 30) < maxLoc[1] < 4.0 / 8 * (height - 30):
                        cv2.putText(image, 'Red', (x_pos + 5, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                        self.red_light = True

                    # Green light
                    elif 5.5 / 8 * (height - 30) < maxLoc[1] < height - 30:
                        cv2.putText(image, 'Green', (x_pos + 5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),2)
                        self.green_light = True

                    # yellow light
                    elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
                        cv2.putText(image, 'Yellow', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
                        self.yellow_light = True

        return v


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
        print('hello')
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
