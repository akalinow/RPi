import time, random, sys
from datetime import timedelta

import numpy as np
import cv2

#Nice printout imports
from termcolor import colored

#TensorFlow
import tensorflow as tf
import keras

#Pandas
import pandas as pd

#Kaggle
import kagglehub

sys.path.append("../python")

#ToF sensor
import VL53L0X

#Ligh sensor
import TSL2591

from Prometheus import Prometheus
from Camera import Camera
from Detector import Detector
from Servos import Servos   
from Identification import Identificator
from image_functions import *

class Monitor:

    def __init__(self):

        #Camera control class
        self.picam = Camera()

        #Face detector class
        self.detector = Detector('blaze_face_short_range.tflite')

        #Servo control class
        self.servos = Servos() 
        self.servos.setPosition((150,30))
        status = self.servos.loadPosition()
        print(colored("Servo position recovery status", "blue"), status)

        #Face identification class
        self.identificatorObj = Identificator()

        #Prometheus exporter class
        self.prom = Prometheus()

        #ToF VL53L0X coltrol
        self.tof_sensor = VL53L0X.VL53L0X(i2c_bus=3,i2c_address=0x29)
        self.tof_sensor.open()

        #Light sensor control
        self.light_sensor = TSL2591.TSL2591()

        self.updateInterval = 600 #seconds
        self.last_time = time.monotonic()

        #Initialize images
        self.rgb_face_patch = None
        self.faces = []
        self.image = None
        print("Initialization done.")
    ####################################
    ####################################
    def __del__(self):
    
        self.tof_sensor.close()
        #self.picam.stop()
    ####################################
    ####################################
    def findFaces(self):

        self.image = self.picam.getRGBImage()
        #self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        self.faces = self.detector.getVideoResponse(self.image)
    ####################################
    ####################################
    def followFace(self, iFace):

        if len(self.faces)<=iFace:
            return

        face_pos = self.faces[iFace][0:2]
        camPos = self.servos.getPosition()
        deltaPos = (face_pos - 0.5)*self.picam.getFOV()/2
        faceAngle = camPos + deltaPos
        self.servos.setPosition(faceAngle)
    ####################################
    ####################################
    def saveFace(self, iFace):

        framePath = "frames/full_frame_{}.jpg".format(time.strftime("%d_%b_%Y%H_%M_%S",time.localtime()))
        rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB) #to be removed
        #rgb_image = visualize(rgb_image, self.faces)
        cv2.imwrite(framePath, annotateImage(rgb_image, 1.0))
        
        if len(self.faces)<=iFace:
            self.rgb_face_patch = None
            return
            
        face_patch = cropFace(self.image, self.faces[iFace])
        self.rgb_face_patch = cv2.cvtColor(face_patch, cv2.COLOR_BGR2RGB) #to be removed
        framePath = "frames/face_{}.jpg".format(time.strftime("%d_%b_%Y%H_%M_%S",time.localtime()))
        cv2.imwrite(framePath, annotateImage(self.rgb_face_patch, 1.0))
    ####################################
    ####################################
    def identifyFace(self, iFace):

        if not np.any(self.rgb_face_patch):
            return None
        
        features = self.identificatorObj.getFeatures(self.rgb_face_patch)
        return self.identificatorObj.getIdentification(features).numpy().flatten()[0]
    ####################################
    ####################################
    def getDistance(self):
        
        self.tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)
        distance = self.tof_sensor.get_distance()/10 #cm
        return distance
    ####################################
    ####################################
    def getLight(self):
        
        return self.light_sensor.Lux
    ####################################
    ####################################
    def sendData(self):

        iFace = 0
        faceId = self.identifyFace(iFace)
        distance = self.getDistance()
        light = self.getLight()
        
        payload = "light="+str(light)+","
        payload +="distance="+str(distance)+","
        if faceId!=None:
            payload +="id="+str(faceId)
            
        self.prom.put(payload)
        
        print(self)
    ####################################
    ####################################
    def run(self):

        iFace = 0
        
        while True:
            
            if self.getLight()<20:
                print(colored("No light. Goint to sleep for 10'", "blue"))
                self.sendData()
                time.sleep(600)
                
            self.findFaces()
            self.followFace(iFace)

            if time.monotonic() - self.last_time>self.updateInterval:
                self.last_time = time.monotonic()
                self.saveFace(iFace)
                self.sendData()
                #break
            
    ####################################
    ####################################
    def __str__(self): 

        message = ""
        message += colored("Light: ","blue") + str(self.getLight()) + " lux "
        message += colored("Distance: ","blue") + str(self.getDistance()) + " cm " 
        message += colored("Face id: ","blue") + str(self.identifyFace(0))
        #message += "\n"
        return message

########################################
########################################
def test_module():            
            
    if __name__ == '__main__':  
        monitorObj = Monitor()
        monitorObj.run()

##################################
test_module() 
