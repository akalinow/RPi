import time

from Camera import Camera
from Detector import Detector
from Servos import Servos   
from image_functions import visualize, drawFocusPoints

import numpy as np
import cv2

#Nice printout imports
from termcolor import colored

#TensorFlow
import tensorflow as tf

#Kaggle
import kagglehub

###################################
def test():

    kaggle_model_path = "google/mobilenet-v3/tfLite/large-100-224-feature-vector"
    model_path = kagglehub.model_download(kaggle_model_path)
    print(colored("Model path:","blue"),model_path)
    interpreter = tf.lite.Interpreter(model_path=model_path+"/1.tflite")
    interpreter.allocate_tensors()

    picam = Camera()
    detector = Detector('/home/akalinow/scratch/FaceFollow/detector.tflite')
    servos = Servos()
    servos.setPosition((90,85)) 

    picamv2_fov = np.array((60, 30))
    deltaPos = np.zeros(2)
    
    while True:
        start_time = time.time()
        time.sleep(0.2)
        image = picam.getRGBImage()
        faces = detector.getVideoResponse(image)

        if len(faces) > 0:
            face_pos = faces[0][0:2]
            print("\r",face_pos, end=' ',)

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
            _ROW_SIZE = 15  # pixels
            _LEFT_MARGIN = 5  # pixels
            _TEXT_COLOR = (0, 0, 255)  # red
            _FONT_SIZE = 1
            _FONT_THICKNESS = 1
            fps_text = 'FPS = ' + str(int(fps))
            text_location = (_LEFT_MARGIN, _ROW_SIZE)
            cv2.putText(rgb_annotated_image, fps_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                _FONT_SIZE, _TEXT_COLOR, _FONT_THICKNESS)

            cv2.imwrite("test_annotated.jpg", rgb_annotated_image)

            input_data = np.expand_dims(annotated_image/255, axis=0).astype(np.float32)
            input = interpreter.get_input_details()[0]
            output = interpreter.get_output_details()[0]
            interpreter.set_tensor(input['index'], input_data)
            interpreter.invoke()
            output = interpreter.get_tensor(output['index'])
            print(output)

        #break 
        else:
            cv2.imwrite("test_annotated.jpg", image)

    print("")

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