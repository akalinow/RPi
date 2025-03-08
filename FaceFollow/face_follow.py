import time, random, sys

from Camera import Camera
from Detector import Detector
from Servos import Servos   
from image_functions import *

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


##########################################
picam = Camera()
detector = Detector('blaze_face_short_range.tflite')
servos = Servos() 
servos.setPosition((150,30))
###########################################
def sweepCamera():

    initAngle = (150,30)

    step = 15 ##degrees
    for iStep in range(50):
        iXStep = random.randint(-3,3)
        iYStep = random.randint(-4,4)
        if iStep==0:
            testAngle = initAngle
        else:
            testAngle = initAngle + step*np.array((iXStep,iYStep))
        servos.setPosition(testAngle)
        time.sleep(0.25)
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

    id_model = keras.saving.load_model("model_A_vs_W.keras")

    kaggle_model_path = "google/mobilenet-v3/tfLite/large-100-224-feature-vector"
    model_path = kagglehub.model_download(kaggle_model_path)
    print(colored("Model path:","blue"),model_path)
    interpreter = tf.lite.Interpreter(model_path=model_path+"/1.tflite")
    interpreter.allocate_tensors()
    featuresShape = interpreter.get_output_details()[0]['shape']

    ###
    df = createEmptyDataset(featuresShape)
    df.to_parquet('df.parquet.gzip',compression='gzip') 
    ###
    '''
    file_path = '/home/akalinow/scratch/RPi/FaceFollow/df.parquet_Artur.gzip'
    df = pd.read_parquet(file_path)
    features = df.drop(columns=['date',label'])
    '''
    nExamples = len(df)

    picamv2_fov = np.array((60, 30))
    deltaPos = np.zeros(2)

    initialCamPos = sweepCamera()
    if initialCamPos is None:
        return
    
    servos.setPosition(initialCamPos)
    
    while True:
        start_time = time.time()
        time.sleep(0.5)
        image = picam.getRGBImage()
        faces = detector.getVideoResponse(image)

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

            # Show the FPS
            # Visualization parameters
            end_time = time.time()
            fps = 1.0 / (end_time - start_time)
            draw_fps(rgb_annotated_image, fps)
            cv2.imwrite("test_annotated_with_face.jpg", rgb_annotated_image)
            ######################################################

            #Identify face
            input_data = np.expand_dims(annotated_image/255, axis=0).astype(np.float32)
            input = interpreter.get_input_details()[0]
            output = interpreter.get_output_details()[0]
            interpreter.set_tensor(input['index'], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output['index'])
            response = id_model(output)
            label = (response<10).numpy().astype(int)

            if len(df)-nExamples<10:             
                label = np.array(label.flatten())
                date = np.array(pd.Timestamp.now())
                dataRow = np.hstack((date, label, output.flatten()))
                df.loc[len(df)] = dataRow
                print(colored("\rNumber of examples:","blue"),len(df), end="")
                sys.stdout.flush()
            else:
                break
            #######################################################
        else:
            cv2.imwrite("test_annotated_without_face.jpg", image)

    lastPos = servos.getPosition()
    print(colored("Last camera position:","blue"),lastPos)
    print(colored("Person presence:","blue"))
    print(df["label"].describe())
    df.to_parquet('df.parquet.gzip',
                   compression='gzip')  

###################################
test()
