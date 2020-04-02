import cv2
import numpy as np
import socket
from model import NeuralNetwork
import threading
import math

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
		self.nn.load_modelSign("sign_model.p")

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

					img =cv2.equalizeHist(gray)
					img = img/255
					img = img.reshape(1, 32, 32, 1)

					classIndex, probability = self.nn.predictSign(img)
					if probability>0.75:
						if   classIndex == 0: self.roadSign = "Stop Sign"
			            elif classIndex == 1: self.roadSign = "No Entry"
			            elif classIndex == 2: self.roadSign = "Green Light"
			            elif classIndex == 3: self.roadSign = "Red Light"
						cv2.putText(image, str(self.roadSign), (20, 35), font, 0.75, (0, 0, 255), 2, cv2.LINE_AA)

					# lower half of the image
					height, width = gray.shape
					roi = gray[int(height/2):height, :]

					cv2.imshow('RPi Camera Stream', image)
					cv2.waitKey(1)

					# reshape image
					image_array = roi.reshape(1, int(height/2) * width).astype(np.float32)
					
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

if __name__ == '__main__':
	# host, port
	h, p = "192.168.0.100", 1234    #laptop

	# model path
	path = "model_test.h5"
  
	rc = RCDriverNNOnly(h, p, path)
	rc.drive()





	