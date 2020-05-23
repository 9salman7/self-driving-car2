#ultrasonic and car status 

import cv2
import numpy as np
import socket
from model import NeuralNetwork
import threading
import math
import time

sensor_data = None

class RCDriverNNOnly(object):

	def __init__(self, host, port, model_path):

		self.server_socket = socket.socket()
		self.server_socket.bind((host, port))
		self.server_socket.listen(0)

		# accept a single connection
		self.connection = self.server_socket.accept()[0].makefile('rb')
		
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.connect(('192.168.0.114', 1234))   #pi for camera

		self.server_socket2 = socket.socket()
		self.server_socket2.bind((host, 4321))
		self.server_socket2.listen(0)

		# accept a single connection
		self.connection2 = self.server_socket2.accept()[0].makefile('rb')
		


		"""self.server_socket2 = socket.socket()
		self.server_socket2.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.server_socket2.bind(("192.168.0.114", 4321))	  #pi for ultrasonic sensor
		self.server_socket2.listen(0)
		self.connection2, self.client_address2 = self.server_socket2.accept()"""
		
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

		self.d_sensor_thresh = 30
		
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

	def sensor_stream(self, host, port):
		global sensor_data
		try:
			start = time.time()

			while True:
				sensor_data = float(self.connection.read(1024))
				print("Distance: %0.1f cm" % sensor_data)

		finally:
			self.connection2.close()
			self.server_socket2.close()
	
	def drive(self):
		sensor_thread = threading.Thread(target=self.sensor_stream, args=(1234, 1234))
		sensor_thread.daemon = True
		sensor_thread.start()
		stop_flag = False
		stop_sign_active = True
		stream_bytes = b' '
		try:
			start = time.time()
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
					cv2.imwrite("camera.jpg", image)

					# reshape image
					image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)

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
						#f = open("status.txt", "w")
						#f.write("Car moving normally")
						#f.close()
						# neural network makes prediction                   
						self.prediction = self.nn.predictKeras(image_array)
						#print("Keras prediction: ",self.prediction)
						
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
			self.connection.close()
			self.server_socket.close()

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
		# 	f = open("status.txt", "w")
		# 	f.write("Car stopped")
		# 	f.close()
		
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
				cv2.putText(image, 'Traffic Light', (x_pos + 5, y_pos - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

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
	# host, port
	h, p = "192.168.0.103", 1234    #laptop

	# model path
	path = "model_test.h5"
  
	rc = RCDriverNNOnly(h, p, path)
	rc.drive()





	