__author__ = 'zhengwang'

import serial
import pygame
from pygame.locals import *
import wiringpi


class RCTest(object):

    def __init__(self):
        pygame.init()
        pygame.display.set_mode((250, 250))
        #self.ser = serial.Serial("/dev/tty.usbmodem1421", 115200, timeout=1)    # mac
        #self.ser = serial.Serial("/dev/ttyAMA0", 115200, timeout=1)           # linux
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
                        #self.ser.write(chr(6).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 1)                
        
                    elif key_input[pygame.K_UP] and key_input[pygame.K_LEFT]:
                        print("Forward Left")
                        #self.ser.write(chr(7).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_RIGHT]:
                        print("Reverse Right")
                        #self.ser.write(chr(8).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    elif key_input[pygame.K_DOWN] and key_input[pygame.K_LEFT]:
                        print("Reverse Left")
                        #self.ser.write(chr(9).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    # simple orders
                    elif key_input[pygame.K_UP]:
                        print("Forward")
                      #  self.ser.write(chr(1).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 1)

                    elif key_input[pygame.K_DOWN]:
                        print("Reverse")
                    #    self.ser.write(chr(2).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 0)

                    elif key_input[pygame.K_RIGHT]:
                        print("Right")
                    #    self.ser.write(chr(3).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 1)
                        wiringpi.digitalWrite(24, 1)

                    elif key_input[pygame.K_LEFT]:
                        print("Left")
                    #    self.ser.write(chr(4).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 1)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 0)
                        
                    elif key_input[pygame.K_s]:
                        print("Stop")
                    #    self.ser.write(chr(4).encode())
                        wiringpi.digitalWrite(21, 0)
                        wiringpi.digitalWrite(22, 0)
                        wiringpi.digitalWrite(23, 0)
                        wiringpi.digitalWrite(24, 0)
                    

                    # exit
                    elif key_input[pygame.K_x] or key_input[pygame.K_q]:
                        print("Exit")
                        self.send_inst = False
                        #self.ser.write(chr(0).encode())
                        #self.ser.close()
                        break

              #  elif event.type == pygame.KEYUP:
               #     self.ser.write(chr(0).encode())


if __name__ == '__main__':
    wiringpi.wiringPiSetup()
    wiringpi.pinMode(21, 1) 
    wiringpi.pinMode(22, 1)
    wiringpi.pinMode(23, 1)
    wiringpi.pinMode(24, 1) 
    RCTest()
