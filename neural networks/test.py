#taken from hamuchiwa github

import cv2
import sys
import threading
import socketserver
import numpy as np
import math
import time
import socket

from model import NeuralNetwork

# distance data measured by ultrasonic sensor
sensor_data = None

class SensorDataHandler(socketserver.BaseRequestHandler):

    data = " "

    def handle(self):
        global sensor_data
        while self.data:
            self.data = self.request.recv(1024)
            sensor_data = round(float(self.data), 1)
            # print "{} sent:".format(self.client_address[0])
            print("Distance: ",sensor_data)

class VideoStreamHandler(socketserver.StreamRequestHandler):
    
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.0.114', 1234))   #pi ip for sending data

    h1 = 5.5  # cm

    # load trained neural network
    nn = NeuralNetwork()
    nn.load_modelKeras("model_test.h5")

    # cascade classifiers
    stop_cascade = cv2.CascadeClassifier(cv2.data.haarcascades +"stop_sign.xml")
    
     # hard coded thresholds for stopping, sensor 30cm, other two 25cm
    d_sensor_thresh = 30
    d_stop_light_thresh = 70
    d_stop_sign = d_stop_light_thresh
    
    stop_start = 0  # start time when stop at the stop sign
    stop_finish = 0
    stop_time = 0
    drive_time_after_stop = 0

    red_light = False
    green_light = False
    yellow_light = False

    alpha = 8.0 * math.pi / 180    # degree measured manually
    v0 = 119.865631204             # from camera matrix
    ay = 332.262498472             # from camera matrix

    def handle(self):
        global sensor_data
        stream_bytes = b' '
        stop_flag = False
        stop_sign_active = True

        try:
            start = time.time()
            # stream video frames one by one
            while True:
                stream_bytes += self.rfile.read(1024)
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

                    # object detection
                    v_param1 = self.detect(self.stop_cascade, gray, image)
                   
                    # distance measurement
                    if v_param1 > 0:
                        d1 = self.calculate(v_param1, self.h1, 300, image)
                        self.d_stop_sign = d1

                    cv2.imshow('RPi Camera Stream', image)
                    cv2.waitkey(1)
                    cv2.imwrite("camera.jpg", image)

                    # reshape image
                    image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)

                    # stop conditions
                    if sensor_data and int(sensor_data) < self.d_sensor_thresh:
                        f = open("status.txt", "w")
                        f.write("Stop, obstacle in front")
                        f.close()
                        print("Stop, obstacle in front")
                        label = "3"
                        self.sendPrediction(label)
                        sensor_data = None

                    elif 0 < self.d_stop_sign < self.d_stop_light_thresh and stop_sign_active:
                        f = open("status.txt", "w")
                        f.write("Stop sign ahead")
                        f.close()   
                        print("Stop sign ahead")
                        label = "3"
                        self.sendPrediction(label)

                        # stop for 5 seconds
                        if stop_flag is False:
                            self.stop_start = cv2.getTickCount()
                            stop_flag = True
                        self.stop_finish = cv2.getTickCount()

                        self.stop_time = (self.stop_finish - self.stop_start) / cv2.getTickFrequency()
                        print("Stop time: %.2fs" % self.stop_time)

                        # 5 seconds later, continue driving
                        if self.stop_time > 5:
                            f = open("status.txt", "w")
                            f.write("Waited for 5 seconds")
                            f.close()
                            print("Waited for 5 seconds")
                            stop_flag = False
                            stop_sign_active = False

                    else:
                        self.prediction = self.nn.predictKeras(image_array)
                        label = self.prediction[0]
                        label = str(label)
                        self.sendPrediction(label)

                        self.stop_start = cv2.getTickCount()
                        self.d_stop_sign = self.d_stop_light_thresh

                        if stop_sign_active is False:
                            self.drive_time_after_stop = (self.stop_start - self.stop_finish) / cv2.getTickFrequency()
                            if self.drive_time_after_stop > 5:
                                stop_sign_active = True

                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Car stopped")
                        self.sendPrediction("3")
                        break
        finally:
            cv2.destroyAllWindows()
            sys.exit()

    def sendPrediction(self, pred):
        if pred == "0":
            f = open("status.txt", "w")
            f.write("Car moving left")
            f.close()
        elif pred == "1":
            f = open("status.txt", "w")
            f.write("Car moving right")
            f.close()
        elif pred == "2":
            f = open("status.txt", "w")
            f.write("Car moving forward")
            f.close()       
        # else:
        #   f = open("status.txt", "w")
        #   f.write("Car stopped")
        #   f.close()
        
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

        return v


class Server(object):
    def __init__(self, host, port1, port2):
        self.host = host
        self.port1 = port1
        self.port2 = port2

    def video_stream(self, host, port):
        s = socketserver.TCPServer((host, port), VideoStreamHandler)
        s.serve_forever()

    def sensor_stream(self, host, port):
        s = socketserver.TCPServer((host, port), SensorDataHandler)
        s.serve_forever()

    def start(self):
        sensor_thread = threading.Thread(target=self.sensor_stream, args=(self.host, self.port2))
        sensor_thread.daemon = True
        sensor_thread.start()
        self.video_stream(self.host, self.port1)


if __name__ == '__main__':
    h, p1, p2 = "192.168.0.103", 1234, 4321

    ts = Server(h, p1, p2)
    ts.start()