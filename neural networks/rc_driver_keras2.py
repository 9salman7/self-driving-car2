import serial
import cv2
import math
import wiringpi
import RPi.GPIO as GPIO
import socket


class RCControl(object):

	def __init__(self):

		self.server_socket = socket.socket()
		self.server_socket.bind(('192.168.0.105', 1234))
		self.server_socket.listen(0)

		# accept a single connection
		#self.connection = self.server_socket.accept()[0].makefile('rb')


		self.connection = self.server_socket.accept()

		wiringpi.wiringPiSetup()
		wiringpi.pinMode(21, 1) 
		wiringpi.pinMode(22, 1)
		wiringpi.pinMode(23, 1)
		wiringpi.pinMode(24, 1)
		
		GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(8, GPIO.OUT, initial= GPIO.LOW)  #left
		GPIO.setup(4, GPIO.OUT, initial= GPIO.LOW)  #red
		GPIO.setup(7, GPIO.OUT, initial= GPIO.LOW)  #right

	def steer(self):
		try:
			while(True):
				sep = ' '
				buf = ''
				while sep not in buf:
					buf+=connection.recv(8)
				prediction=int(buf)
				
				if prediction == 2:
					#self.serial_port.write(chr(1).encode())
					print("Forward")
					wiringpi.digitalWrite(21, 0)
					wiringpi.digitalWrite(22, 0)
					wiringpi.digitalWrite(23, 0)
					wiringpi.digitalWrite(24, 1)
					
					GPIO.output(8, GPIO.LOW) # Turn on
					GPIO.output(7, GPIO.LOW) # Turn on
					GPIO.output(4, GPIO.LOW)

				elif prediction == 0:
					#self.serial_port.write(chr(7).encode())
					print("Left")
					wiringpi.digitalWrite(21, 0)
					wiringpi.digitalWrite(22, 1)
					wiringpi.digitalWrite(23, 0)
					wiringpi.digitalWrite(24, 0)\
											  
					GPIO.output(8, GPIO.HIGH) # Turn on
					GPIO.output(7, GPIO.LOW) # Turn on
					GPIO.output(4, GPIO.LOW)

				elif prediction == 1:
					#self.serial_port.write(chr(6).encode())
					print("Right")
					wiringpi.digitalWrite(21, 0)
					wiringpi.digitalWrite(22, 0)
					wiringpi.digitalWrite(23, 1)
					wiringpi.digitalWrite(24, 1)
					
					GPIO.output(8, GPIO.LOW) # Turn on
					GPIO.output(7, GPIO.HIGH) # Turn on
					GPIO.output(4, GPIO.LOW)

				else:
					self.stop()
					#print("Stop")
					wiringpi.digitalWrite(21, 0)
					wiringpi.digitalWrite(22, 0)
					wiringpi.digitalWrite(23, 0)
					wiringpi.digitalWrite(24, 0)

					GPIO.output(8, GPIO.LOW) # Turn on
					GPIO.output(7, GPIO.LOW) # Turn on
					GPIO.output(4, GPIO.HIGH)
		finally:
			#self.connection.close()
			self.server_socket.close()


	def stop(self):
		#self.serial_port.write(chr(0).encode())
		#print("Stop")
		wiringpi.digitalWrite(21, 0)
		wiringpi.digitalWrite(22, 0)
		wiringpi.digitalWrite(23, 0)
		wiringpi.digitalWrite(24, 0)

		GPIO.output(8, GPIO.LOW) # Turn on
		GPIO.output(7, GPIO.LOW) # Turn on
		GPIO.output(4, GPIO.HIGH)


if __name__ == '__main__':
	rc=RCControl()
	rc.steer()







"""class DistanceToCamera(object):

	def __init__(self):
		# camera params
		self.alpha = 8.0 * math.pi / 180    # degree measured manually
		self.v0 = 119.865631204             # from camera matrix
		self.ay = 332.262498472             # from camera matrix

	def calculate(self, v, h, x_shift, image):
		# compute and return the distance from the target point to the camera
		d = h / math.tan(self.alpha + math.atan((v - self.v0) / self.ay))
		if d > 0:
			cv2.putText(image, "%.1fcm" % d,
						(image.shape[1] - x_shift, image.shape[0] - 20),
						cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
		return d

class ObjectDetection(object):

	def __init__(self):
		self.red_light = False
		self.green_light = False
		self.yellow_light = False

	def detect(self, cascade_classifier, gray_image, image):

		# y camera coordinate of the target point 'P'
		v = 0

		# minimum value to proceed traffic light state validation
		threshold = 150

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

			# traffic lights
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
					# elif 4.0/8*(height-30) < maxLoc[1] < 5.5/8*(height-30):
					#    cv2.putText(image, 'Yellow', (x_pos+5, y_pos - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2)
					#    self.yellow_light = True
		return v
"""