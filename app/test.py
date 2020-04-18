import numpy as np
import cv2
from playsound import playsound 

ESC=27

camera = cv2.VideoCapture(0)
orb = cv2.ORB_create(nfeatures=1500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

def myFunction():
    # camera = cv2.VideoCapture(0)
    # orb = cv2.ORB_create(nfeatures=1500)
    # bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    rTrainColor=cv2.imread('redlight.jpg') 
    rTrainGray = cv2.cvtColor(rTrainColor, cv2.COLOR_BGR2GRAY)

    gTrainColor=cv2.imread('greenlight.jpg') 
    gTrainGray = cv2.cvtColor(gTrainColor, cv2.COLOR_BGR2GRAY)

    rkpTrain = orb.detect(rTrainGray,None)
    rkpTrain, rdesTrain = orb.compute(rTrainGray, rkpTrain)

    gkpTrain = orb.detect(gTrainGray,None)
    gkpTrain, gdesTrain = orb.compute(gTrainGray, gkpTrain)

    firsttime=True
    rdetected = False
    gdetected = False

    while True:

   
        ret, imgCamColor = camera.read()
        imgCamGray = cv2.cvtColor(imgCamColor, cv2.COLOR_BGR2GRAY)
        kpCam = orb.detect(imgCamGray,None)
        kpCam, desCam = orb.compute(imgCamGray, kpCam)

        rmatches = bf.match(desCam,rdesTrain)
        rdist = [rm.distance for rm in rmatches]
        rthres_dist = (sum(rdist) / len(rdist)) * 0.5
        rmatches = [rm for rm in rmatches if rm.distance < rthres_dist]

        gmatches = bf.match(desCam,gdesTrain)
        gdist = [gm.distance for gm in gmatches]
        gthres_dist = (sum(gdist) / len(gdist)) * 0.5
        gmatches = [gm for gm in gmatches if gm.distance < gthres_dist]

        if len(rmatches)>4 or len(gmatches)>4:
            if len(rmatches)>len(gmatches) and rdetected == False:
                print("Red light ahead")
                rdetected = True
                gdetected = False
                f = open("status.txt", "w")
                f.write("Red light ahead")
                f.close()
                #playsound("redlight.mp3")
                #cv2.imshow('match',rTrainColor)
                
            elif len(rmatches)<len(gmatches) and gdetected == False:
                print("Green light ahead")
                rdetected = False
                gdetected = True
                f = open("status.txt", "w")
                f.write("Green light ahead")
                f.close()
                #playsound("greenlight.mp3")
                #cv2.imshow('match',gTrainColor)

        if(rdetected == True):
            cv2.putText(imgCamColor, "Red Light Ahead!" , (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2, cv2.LINE_AA)
        elif(gdetected == True):
            cv2.putText(imgCamColor, "Green Light Ahead!" , (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2, cv2.LINE_AA)
                
        cv2.imshow('Traffic Signal Detection', imgCamColor)
        cv2.imwrite("camera.jpg",imgCamColor)
        
        ch = 0xFF & cv2.waitKey(1)
        if ch == 27:
           break
        
myFunction()
camera.release()
cv2.destroyAllWindows()




    
    
