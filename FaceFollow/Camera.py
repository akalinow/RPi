#!/usr/bin/python
import time

#Nice printout imports
from termcolor import colored # type: ignore

#Picamera imports
from picamera2 import MappedArray, Picamera2, Preview
from libcamera import Transform

# CV2 imports
import cv2

class Camera:

    normalSize = (2*640, 2*480)

    ####################################
    def __init__(self):

        self.picam = Picamera2()
        config_still = self.picam.create_still_configuration(main={"format": 'XRGB8888', 
                                                             "size": self.normalSize},
                                        transform = Transform(hflip=False, vflip=True))     

        config_video = self.picam.create_video_configuration(main={"format": 'XRGB8888', 
                                                             "size": self.normalSize},
                                        transform = Transform(hflip=False, vflip=True))                                

                                                             
        self.picam.configure(config_video)
        self.picam.start() 
        time.sleep(1)
    ################################
    def __del__(self): 
        self.picam.stop()
    ################################
    def getFile(self, filename):
        self.picam.capture_file(filename)
    ################################
    def getRGBImage(self):

        image = self.picam.capture_array()       
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        return rgb_image
 
    #################################
    def __str__(self): 
        message = (colored("Camera:","blue")+"{}").format(self.picam.still_configuration)
        return message    

#################################   
#################################  
def test_module():            
            
    if __name__ == '__main__':  
        cameraObj = Camera()
        cameraObj.getFile("test.jpg")
        image = cameraObj.getRGBImage()
        
        print(image.shape)
        print(cameraObj)   
##################################
test_module()



