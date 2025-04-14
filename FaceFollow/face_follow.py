import time, random, sys
from datetime import timedelta

from Camera import Camera
from Detector import Detector
from Servos import Servos   
from Identification import Identificator
from Display import Display
from image_functions import *

import numpy as np
import cv2

sys.path.append("../python")

#ToF sensor
import VL53L0X

#Ligh sensor
import TSL2591

#Nice printout imports
from termcolor import colored

#TensorFlow
import tensorflow as tf
import keras

#Pandas
import pandas as pd

#Kaggle
import kagglehub


##########################################
picam = Camera()
detector = Detector('blaze_face_short_range.tflite')
servos = Servos() 
servos.setPosition((150,30))
status = servos.loadPosition()
print(colored("Camera position recovery status", "blue"), status)
display = Display()
###########################################
def sweepCamera(initAngle):

    step = 15 ##degrees
    for iStep in range(50):
        iXStep = random.randint(-3,3)
        iYStep = random.randint(-4,4)
        if iStep==0:
            testAngle = initAngle
        else:
            testAngle = initAngle + step*np.array((iXStep,iYStep))
        servos.setPosition(testAngle)
        face = []
        for iTry in range(4):
            time.sleep(0.1)
            image = picam.getRGBImage()
            faces = detector.getVideoResponse(image)
        print("\r",testAngle, end=' ',)
        print("\r",len(faces), end=' ',)
        if len(faces) > 0:
           return testAngle

    servos.setPosition(initAngle)
    return None
###################################
def createEmptyDataset(featuresShape):

    dummyOutput = np.zeros(featuresShape).flatten()
    dummyLabel = np.array((-1))
    date = np.array(pd.Timestamp.now())
    dataRow = np.hstack((date, dummyLabel, dummyOutput)).reshape(1,-1)
    df = pd.DataFrame(data=dataRow, columns=["date", "label"]+["feature_"+str(i) for i in range((dataRow.size-2)) ])
    return df
###################################
def test():

    identificatorObj = Identificator()
    featuresShape =  identificatorObj.getFeaturesShape()
    
    df = createEmptyDataset(featuresShape)
    df.to_parquet('df.parquet.gzip',compression='gzip') 
    nExamples = len(df)

    picamv2_fov = np.array((60, 30))
    deltaPos = np.zeros(2)

    initialCamPos = sweepCamera(servos.getPosition())
    if initialCamPos is None:
        return
    
    servos.setPosition(initialCamPos)

    # Create a VL53L0X object
    tof_sensor = VL53L0X.VL53L0X(i2c_bus=3,i2c_address=0x29)
    #tof_sensor.open()
    #tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)

    # Create light sensor
    light_sensor = TSL2591.TSL2591()

    last_time = time.monotonic()
    updateInterval = 60 #seconds
    while True:
        start_time = time.time()
        ####
        if time.monotonic() - last_time>updateInterval:

            #tof_sensor.stop_ranging()
            #tof_sensor.close()
            #tof_sensor.open()
            #tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)
            #print("AAA")
            last_time = time.monotonic()
        #### 
        '''
        camPos = sweepCamera(servos.getPosition())
        if np.all(camPos)!=None:
            servos.setPosition(camPos)
        else:
            continue
        '''
        
        image = picam.getRGBImage()
        faces = detector.getVideoResponse(image)

        lux = light_sensor.Lux
        distance = -1 #tof_sensor.get_distance()/10 #cm

        print(colored(" Light:","blue"), lux, colored("Distance:","blue"), distance)

        if len(faces) > 0:
            face_pos = faces[0][0:2]
            #print("\r",face_pos, end=' ',)

            camPos = servos.getPosition()
            deltaPos += (face_pos - 0.5)*picamv2_fov
            deltaPos /= 2
            faceAngle = camPos + deltaPos
            servos.setPosition(faceAngle)

            annotated_image = drawFocusPoints(image, faces)
            rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)

            # Visualization parameters
            end_time = time.time()
            fps = 1.0 / (end_time - start_time)
            #draw_fps(rgb_annotated_image, fps)
            cv2.imwrite("test_annotated_with_face.jpg", rgb_annotated_image)
            ######################################################

            #Identify face
            features = identificatorObj.getFeatures(rgb_annotated_image)
            idendity = identificatorObj.getIdentification(features).numpy().flatten()
            print(colored("Face Id label:","blue"),idendity)
            message = "Id: {:3.2f}".format(idendity)
            display.displayName(message)

            #Save face data
            if len(df)-nExamples<500:
                label = 0
                date = np.array(pd.Timestamp.now())
                dataRow = np.hstack((date, idendity, features.flatten()))
                df.loc[len(df)] = dataRow
                print(colored("\rNumber of examples:","blue"),len(df), end="")
                sys.stdout.flush()
            else:
                break
            #######################################################
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            draw_fps(image, fps)
            cv2.imwrite("test_annotated_without_face.jpg", image)

    tof_sensor.stop_ranging()
    tof_sensor.close()
    
    servos.savePosition()

    print(colored("Person presence:","blue"))
    print(df["label"].describe())
    df.to_parquet('df.parquet.gzip',
                   compression='gzip')  

###################################
test()
