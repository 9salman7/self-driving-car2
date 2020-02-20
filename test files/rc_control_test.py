import pygame
from pygame.locals import *
import wiringpi
import RPi.GPIO as GPIO



class RCTest(object):

    def __init__(self):
        pygame.init()
        pygame.display.set_mode((250, 250))
       
        pygame.display.update()
        self.send_inst = True
        self.steer()

    def steer(self):

        while self.send_inst:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    key_input = pygame.key.get_pressed()

                    # complex orders
                    if key_input[pygame.K_UP] and key_input[pygame.K_RIGHT]:
                        print("Forward Right")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 1)                
        
                    elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                        print("Forward Left")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                        print("Reverse Right")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                        print("Reverse Left")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    # simple orders
                    elif key_input[pygame.K_UP]:
                        print("Forward")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 1)
                        GPIO.output(8, GPIO.LOW) # Turn on
                        GPIO.output(7, GPIO.LOW) # Turn on
                        GPIO.output(4, GPIO.LOW)
                                                
                    elif key_input[pygame.K_DOWN]:
                        print("Reverse")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)
                        
                        GPIO.output(8, GPIO.HIGH) # Turn on
                        GPIO.output(7, GPIO.HIGH) # Turn on
                        GPIO.output(4, GPIO.LOW)

                    elif key_input[pygame.K_RIGHT]:
                        print("Right")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 1)
                        
                        GPIO.output(8, GPIO.LOW) # Turn on
                        GPIO.output(7, GPIO.HIGH) # Turn on
                        GPIO.output(4, GPIO.LOW)

                    elif key_input[pygame.K_LEFT]:
                        print("Left")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 0)
                        
                        GPIO.output(8, GPIO.HIGH) # Turn on
                        GPIO.output(7, GPIO.LOW) # Turn on
                        GPIO.output(4, GPIO.LOW)
                        
                    elif key_input[pygame.K_s] or key_input[pygame.K_SPACE]:
                        print("Stop")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 0)
                    
                        GPIO.output(8, GPIO.LOW) # Turn on
                        GPIO.output(7, GPIO.LOW) # Turn on
                        GPIO.output(4, GPIO.HIGH)                    
                    # exit
                    elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                        print("Exit")
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 1)
                        
                        GPIO.output(8, GPIO.LOW) # Turn on
                        GPIO.output(7, GPIO.LOW) # Turn on
                        GPIO.output(4, GPIO.LOW) 
                        self.send_inst = False
                        break

              #  elif event.type == pygame.KEYUP:
               #     self.ser.write(chr(0).encode())


if __name__ == '__main__':
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
    
    RCTest()
