#System imports
import time

import numpy as np
import cv2

#Nice printout imports
from termcolor import colored

#TensorFlow
import tensorflow as tf
import keras

#Kaggle
import kagglehub

class Identificator:

    def __init__(self, features_model_path="google/mobilenet-v3/tfLite/large-100-224-feature-vector", 
                 id_model_path="model_A_vs_W.keras"):

        self.id_model = keras.saving.load_model(id_model_path)
        model_path = kagglehub.model_download(features_model_path)
        print(colored("Model path:","blue"),model_path)
        self.features_model = tf.lite.Interpreter(model_path=model_path+"/1.tflite")
        self.features_model.allocate_tensors()
    #############################################
    def getFeaturesShape(self):
        return self.features_model.get_output_details()[0]['shape']
    #############################################
    def getFeatures(self, rgb_image):

        input = self.features_model.get_input_details()[0]
        output = self.features_model.get_output_details()[0]

        input_data = np.expand_dims(rgb_image/255, axis=0).astype(np.float32)
        self.features_model.set_tensor(input['index'], input_data)  
        self.features_model.invoke()
        output = self.features_model.get_tensor(output['index'])
        return output
    #############################################
    def getIdentification(self, features):
        response = self.id_model(features)
        return response
    #############################################
    def getResponse(self, rgb_image):
        
        features = self.getFeatures(rgb_image)
        ids = self.getIdentification(features)
        return ids
        
#############################################
#############################################
def test_module():            
            
    if __name__ == '__main__':  
        images = ['image_AK.jpg', 'image_WK.jpg']
        identificatorObj = Identificator()
        for image in images:
            rgb_image = cv2.imread(image)
            response = identificatorObj.getResponse(rgb_image)
            print(colored("Id mode response to:","blue"), image, response)
          
#############################################
test_module()


