# USAGE
# python webstreaming.py --ip 0.0.0.0 --port 8000

import cv2
import numpy as np
import socket
from model import NeuralNetwork
import threading
import math
from io import BytesIO

from bottle import Bottle, run, route, static_file, request, response, template, redirect, get, post, HTTPResponse, LocalResponse

import argparse
import datetime
import time

outputFrame = None
lock = threading.Lock()

# initialize a flask object
app = Bottle(__name__)

@app.route('/<filename:re:.*\.html>')
def javascripts(filename):
	return static_file(filename, root='templates')

@app.route('/<filename:re:.*\.js>')
def javascripts(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.css>')
def stylesheets(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.(jpg|png|gif|ico|svg)>')
def images(filename):
	return static_file(filename, root='static')

@app.route('/<filename:re:.*\.(eot|ttf|woff|svg)>')
def fonts(filename):
	return static_file(filename, root='static')



@app.route("/")
def index():
	# return the rendered template
	return static_file("index.html", root="templates/")

def generate():
	# grab global references to the output frame and lock variables
	global outputFrame, lock
	# loop over frames from the output stream
	while True:
		# check if the output frame is available, otherwise skip
		# the iteration of the loop
		with lock:
			if outputFrame is None:
				continue

			# encode the frame in JPEG format
			(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

			# ensure the frame was successfully encoded
			if not flag:
				continue

		# yield the output frame in the byte format
		yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
			bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	
	return response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/image")
def image():
	(flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
	response.content_type= "image/jpeg"
	encodedImage = b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n'
	return encodedImage

@app.get('/speechRec')
def speechRec():
	r = sr.Recognizer()
	with sr.Microphone() as source:
		print("Speak Anything: ")
		audio = r.listen(source)
		try:
			text = r.recognize_google(audio)
			print("You said : {}".format(text))
		except:
			print("Could not recognize")

class RCDriverNNOnly(object):

	def __init__(self, host, port, model_path):

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

		self.d_stop_light_thresh = 50
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

		global outputFrame, lock

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

					with lock:
						outputFrame = image.copy()
						
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

if __name__ == '__main__':
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--ip", type=str, required=True,
		help="ip address of the device")
	ap.add_argument("-o", "--port", type=int, required=True,
		help="ephemeral port number of the server (1024 to 65535)")
	args = vars(ap.parse_args())

	h, p = "192.168.0.100", 1234    #laptop

	# model path
	path = "model_test.h5"
  
	rc = RCDriverNNOnly(h, p, path)

	# start a thread that will perform motion detection
	t = threading.Thread(target=rc.drive, args=())
	t.daemon = True
	t.start()

	# start the flask app
	app.run(host=args["ip"], port=args["port"])
	#app.run(host='127.0.0.1', port=8080)
