import time

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

###################################
def test():

    id_model = keras.saving.load_model("model_A_vs_W.keras")

    kaggle_model_path = "google/mobilenet-v3/tfLite/large-100-224-feature-vector"
    model_path = kagglehub.model_download(kaggle_model_path)
    print(colored("Model path:","blue"),model_path)
    interpreter = tf.lite.Interpreter(model_path=model_path+"/1.tflite")
    interpreter.allocate_tensors()

    picam = Camera()
    detector = Detector('blaze_face_short_range.tflite')
    servos = Servos() 
    servos.setPosition((130,40))

    picamv2_fov = np.array((60, 30))
    deltaPos = np.zeros(2)

    '''
    dummyRow = np.zeros((1280)),
    df = pd.DataFrame(data=dummyRow)
    df["label"] = np.full((1), -1)
    df.to_parquet('df.parquet.gzip',compression='gzip') 
    '''
    file_path = '/home/akalinow/scratch/RPi/FaceFollow/df.parquet_Artur.gzip'
    df = pd.read_parquet(file_path)
    features = df.drop(columns=['label'])
    nExamples = len(df)
    
    while True:
        start_time = time.time()
        time.sleep(0.2)
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
            cv2.imwrite("test_annotated.jpg", rgb_annotated_image)
            ######################################################

            #Identify face
            input_data = np.expand_dims(annotated_image/255, axis=0).astype(np.float32)
            input = interpreter.get_input_details()[0]
            output = interpreter.get_output_details()[0]
            interpreter.set_tensor(input['index'], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output['index'])

            response = id_model(output)
            if response<5:
                print(colored("Artur!","blue"))
            elif response>5:
                print(colored("Wojtek!","blue"))
            else:
                print(colored("Unknown!","blue"))

            new_item_label = 0
            new_item_label = np.array(new_item_label).reshape((1,1))
            dataRow = np.concatenate( (output, new_item_label), axis=1)
            df.loc[len(df)+20] = dataRow[0]
            print("Number of examples:",len(df))
            if len(df)-nExamples>500:
                break
            #######################################################
        else:
            cv2.imwrite("test_annotated.jpg", image)

    lastPos = servos.getPosition()
    print("Last camera position:",lastPos)
    print("")
    print(df.describe())
    df.to_parquet('df.parquet.gzip',
                   compression='gzip')  

###################################
test()

'''
face detector result: 
DetectionResult(detections=[Detection(bounding_box=BoundingBox(origin_x=0, origin_y=168, width=366, height=366), 
categories=[Category(index=0, score=0.5604583024978638, display_name=None, category_name=None)], 
keypoints=[
NormalizedKeypoint(x=0.003223732579499483, y=0.7284545302391052, label='', score=0.0), 
NormalizedKeypoint(x=0.24945300817489624, y=0.6111683249473572, label='', score=0.0), 
NormalizedKeypoint(x=0.1393018364906311, y=0.9198736548423767, label='', score=0.0), 
NormalizedKeypoint(x=0.19469484686851501, y=1.0107040405273438, label='', score=0.0), 
NormalizedKeypoint(x=-0.044375721365213394, y=0.7179324626922607, label='', score=0.0), 
NormalizedKeypoint(x=0.44926655292510986, y=0.4869495630264282, label='', score=0.0)])])


'''