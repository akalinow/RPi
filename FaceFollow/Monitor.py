import time, random, sys, datetime
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
from Display import Display
from image_functions import *

class Monitor:

    def __init__(self):

        #Camera control class
        self.picam = Camera()

        #Face detector class
        self.detector = Detector('blaze_face_short_range.tflite')

        #Servo control class
        self.servos = Servos() 
        self.servos.setPosition((95,60))
        status = self.servos.loadPosition()
        print(colored("Servo position recovery status", "blue"), status)

        #Face identification class
        self.identificatorObj = Identificator()

        #Prometheus exporter class
        self.prom = Prometheus()

        #ToF VL53L0X coltrol
        self.tof_sensor = VL53L0X.VL53L0X(i2c_bus=3,i2c_address=0x29)
        self.tof_sensor.open()
        self.tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)

        #Light sensor control
        self.light_sensor = TSL2591.TSL2591()

        #Display
        self.display = Display()

        #Prometheus update rate
        self.updateInterval = 600 #seconds
        self.last_time = -1

        #Initialize images
        self.face_patch = None
        self.faces = []
        self.image = None

        self.reset()
        
        print("Initialization done.")
    ####################################
    ####################################
    def __del__(self):
    
        self.tof_sensor.close()
        #self.picam.stop()
    ####################################
    ####################################
    def reset(self):

        #Face counter
        self.faceIdByFraction = -1
        self.faceFraction = 0.0
        self.faceIndex = -1
        self.faceProb = -1
        self.faceCounter = np.zeros((4,), dtype=np.float32)

        #Face velocity
        self.deltaPos = np.array((0.0, 0.0))

    ####################################
    ####################################
    def findFaces(self):

        self.image = self.picam.getRGBImage()
        self.faces = self.detector.getVideoResponse(self.image)
    ####################################
    ####################################
    def followFace(self, iFace):

        #calculate mean face position
        mean_face_pos = np.array([0.0, 0.0])
        for face in self.faces:
            mean_face_pos += face[0:2]/len(self.faces)
            self.deltaPos = (mean_face_pos - 0.5)*self.picam.getFOV()/2

        #No faces to follow. Continue movement from previous direction
        #i.e. face dissaperaed quickly from the field of view
        if len(self.faces)<1:
            self.deltaPos *=0.6
            
        if np.sum(self.deltaPos**2)<8:
            return

        #update position    
        faceAngle = self.servos.getPosition() + self.deltaPos*1.0
        self.servos.setPosition(faceAngle)
    ####################################
    ####################################
    def cropFace(self, iFace):

        if len(self.faces)<=iFace:
            self.face_patch = None
            return
        
        self.face_patch = cropFace(self.image, self.faces[iFace])
    ####################################
    ####################################
    def saveFace(self):

        framePath = "frames/full_frame_{}.jpg".format(time.strftime("%d_%b_%Y%H_%M_%S",time.localtime()))
        cv2.imwrite(framePath, annotateImage(self.image, 1.0))
        
        if not np.any(self.face_patch):
            return
            
        framePath = "frames/face_{}.jpg".format(time.strftime("%d_%b_%Y%H_%M_%S",time.localtime()))
        cv2.imwrite(framePath, annotateImage(self.face_patch, 1.0))
    ####################################
    ####################################
    def identifyFace(self):

        if not np.any(self.face_patch):
            self.faceIndex = -1
            self.faceProb = -1
            self.faceIdByFraction = -1
            self.faceFraction = -1 
            self.faceCounter[-1]+=1
        else: 
            features = self.identificatorObj.getFeatures(self.face_patch)
            result =  self.identificatorObj.getIdentification(features).numpy()[0]
            self.faceIndex = np.argmax(result)
            self.faceProb = result[self.faceIndex]
            self.faceCounter[self.faceIndex]+=1
            
        self.getFaceIdFraction()
    ####################################
    ####################################
    def getFaceIdFraction(self):

        totalCount = np.sum(self.faceCounter)
        if totalCount<1:
            totalCount = 1
            
        fraction = self.faceCounter/totalCount
     
        index = np.argmax(fraction)
        value = fraction[index]
        self.faceIdByFraction = index
        self.faceFraction = value 
    ####################################
    ####################################
    def getDistance(self):
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
        faceId = self.faceIdByFraction
        fraction = "{:3.2f}".format(self.faceFraction)
        distance = self.getDistance()
        light = self.getLight()
        
        payload = "light="+str(light)
        payload +=",distance="+str(distance)
        payload +=",id="+str(faceId)
        payload +=",fraction="+fraction
            
        self.prom.put(payload)
    ####################################
    ####################################
    def displayData(self):

        idMap = {-1:"Nobody",
                 0: "Artur",
                 1: "Wojtek",
                 2: "Unknown"}

        message =  idMap[self.faceIndex] + "\n"
        message += "p={:3.2f}".format(self.faceProb) 
        message += " f={:3.2f}".format(self.faceFraction) + "\n"
        message += "d={:d} [cm]".format(int(self.getDistance()))
        
        self.display.displayMessage(message)
    ####################################
    ####################################
    def run(self):

        iFace = 0
        
        while True:

            self.findFaces()
            
            if np.mean(self.image)<20:
                print(colored("No light. Going to sleep for 10'", "blue"))
                self.sendData()
                self.reset()
                self.display.clear()
                time.sleep(600)
                
            self.followFace(iFace)
            #Face identification every 10''
            if int(time.monotonic())%10==0:
                self.cropFace(iFace)
                self.identifyFace()
                self.displayData()
                print(self)

            #Send data to Prometheus every self.updateInterval
            if time.monotonic() - self.last_time>self.updateInterval:
                self.last_time = time.monotonic()
                self.saveFace()
                self.sendData()
                if self.faceIdByFraction<len(self.faceCounter)-1:
                    self.servos.savePosition()
                #print(self)
                self.reset()
            
    ####################################
    ####################################
    def __str__(self): 

        message = ""
        message += colored("Light: ","blue") + str(self.getLight()) + " lux "
        message += colored("Distance: ","blue") + str(self.getDistance()) + " cm " 
        message += colored("Face id. Instant: ","blue") + str(self.faceIndex) + " "
        message += colored("by fraction: ","blue") + "{:3.2f}".format(self.faceIdByFraction)
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
