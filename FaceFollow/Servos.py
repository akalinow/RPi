#!/usr/bin/python
import time
from PCA9685 import PCA9685

import numpy as np

#Nice printout imports
from termcolor import colored # type: ignore

class Servos:

    # Movement range [deg]
    angleRange = {"h": (0, 180), "v": (5,95)}

    # Horizontal/Vertical servos id 
    servosId = {"h":0, "v":1}

    # Initial position
    restPos = {"h":165, "v":70}

    ####################################
    def __init__(self):

        # current position
        self.currAngle = self.restPos

        # Servo driver manager
        self.pwm = PCA9685()

        self.resetPosition()

        time.sleep(0.5)

   ################################
    def resetPosition(self):

        self.pwm.setPWMFreq(50)
        self.pwm.setRotationAngle(self.servosId["h"], self.restPos["h"])
        self.pwm.setRotationAngle(self.servosId["v"], self.restPos["v"])
        self.currAngle = self.restPos

    #################################
    def setAxisPosition(self, axis, degrees):

        if degrees>=self.angleRange[axis][0] and degrees<=self.angleRange[axis][1]:
            self.pwm.setRotationAngle(self.servosId[axis], degrees)
            self.currAngle[axis] = degrees

    #################################   
    def setPosition(self, degrees):

        degreesH, degreesV = degrees
        self.setAxisPosition("h", degreesH) 
        self.setAxisPosition("v", degreesV)

    #################################
    def getPosition(self):
        return np.array((self.currAngle["h"], self.currAngle["v"]))
    #################################
    def __str__(self): 
        message = (colored("H:","blue")+"{} "+colored("V:","blue")+"{}").format(self.currAngle["h"], self.currAngle['v'])
        return message    
    #################################
    def savePosition(self, filePath="camera_pos.txt"):
        pos = self.getPosition()
        np.savetxt(filePath, pos, delimiter=" ")
    #################################
    def loadPosition(self, filePath="camera_pos.txt"):
        status = 0
        try:
            with open(filePath) as file:
                pos = np.loadtxt(filePath, delimiter=" ")
                self.setPosition(pos)
                status = 0
        except FileNotFoundError:
            status = -1
        return status
    #################################

#################################   
#################################  
def test_module():            
            
    if __name__ == '__main__':  
        servosObj = Servos()
        servosObj.setPosition((90,85))    
        print(servosObj)  
##################################
test_module()



