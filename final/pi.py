import serial
import cv2
import math
import wiringpi
import RPi.GPIO as GPIO
import socket
import time
import pdb

GPIO.setwarnings(False)

# referring to the pins by GPIO numbers
GPIO.setmode(GPIO.BCM)

# define pi GPIO
GPIO_TRIGGER = 23
GPIO_ECHO    = 24

# output pin: Trigger
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
# input pin: Echo
GPIO.setup(GPIO_ECHO,GPIO.IN)
# initialize trigger pin to low
GPIO.output(GPIO_TRIGGER, False)

time.sleep(2)

class RCControl(object):

	def __init__(self):

		self.server_socket = socket.socket()
		self.server_socket.bind(('192.168.0.114', 1234))    #pi
		self.server_socket.listen(0)
		self.connection= self.server_socket.accept()[0]

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
				buf = b''
				while sep not in buf:
					buf+=self.connection.recv(1024)
				
				prediction = str(buf)
				distance = self.measure()
				#print(distance)
				
				if distance > 30.0 :
					f = open("obstacle.txt", "w")
					f.write("No obstacle ahead")
					f.close()
					if prediction == "2 ":
						print("Forward")
						wiringpi.digitalWrite(21, 0)
						wiringpi.digitalWrite(22, 0)
						wiringpi.digitalWrite(23, 0)
						wiringpi.digitalWrite(24, 1)
						
						GPIO.output(8, GPIO.LOW) # Turn on
						GPIO.output(7, GPIO.LOW) # Turn on
						GPIO.output(4, GPIO.LOW)

					elif prediction == "0 ":
						print("Left")
						wiringpi.digitalWrite(21, 0)
						wiringpi.digitalWrite(22, 1)
						wiringpi.digitalWrite(23, 0)
						wiringpi.digitalWrite(24, 0)
												  
						GPIO.output(8, GPIO.HIGH) # Turn on
						GPIO.output(7, GPIO.LOW) # Turn on
						GPIO.output(4, GPIO.LOW)

					elif prediction == "1 ":
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
						print("Stop")
						wiringpi.digitalWrite(21, 0)
						wiringpi.digitalWrite(22, 0)
						wiringpi.digitalWrite(23, 0)
						wiringpi.digitalWrite(24, 0)

						GPIO.output(8, GPIO.LOW) # Turn on
						GPIO.output(7, GPIO.LOW) # Turn on
						GPIO.output(4, GPIO.HIGH)

				else:
					f = open("obstacle.txt", "w")
					f.write("Obstacle ahead!")
					f.close()
					self.stop()
					print("Obstacle ahead! Distance: ", distance)
					
		finally:
			#self.connection.close()
			self.server_socket.close()
			GPIO.cleanup()

	def stop(self):
		wiringpi.digitalWrite(21, 0)
		wiringpi.digitalWrite(22, 0)
		wiringpi.digitalWrite(23, 0)
		wiringpi.digitalWrite(24, 0)

		GPIO.output(8, GPIO.LOW) # Turn on
		GPIO.output(7, GPIO.LOW) # Turn on
		GPIO.output(4, GPIO.HIGH)

	def measure(self):
		"""
		measure distance
		"""
		GPIO.output(GPIO_TRIGGER, True)
		time.sleep(0.00001)
		GPIO.output(GPIO_TRIGGER, False)
		start = time.time()

		while GPIO.input(GPIO_ECHO)==0:
			start = time.time()

		while GPIO.input(GPIO_ECHO)==1:
			stop = time.time()

		elapsed = stop-start
		distance = (elapsed * 34300)/2
		distance = round(distance, 1)
		return distance


if __name__ == '__main__':
	rc=RCControl()
	rc.steer()
