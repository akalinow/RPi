#!/bin/python3

import time

#Nice printout imports
from termcolor import colored

#Prometheus/Influx io
from Prometheus import Prometheus

#ToF sensor
import VL53L0X

#Ligh sensor
import TSL2591

##################################################
def collect_data():

    # Create a VL53L0X object
    tof_sensor = VL53L0X.VL53L0X(i2c_bus=3,i2c_address=0x29)
    tof_sensor.open()
    tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.BEST)

    # Create light sensor
    light_sensor = TSL2591.TSL2591()

    #Read sensors
    lux = light_sensor.Lux

    nSamples = 10
    distance = 0
    count = 0
    #average measurement over about nSamples
    for iTry in range(nSamples):
        measurement = tof_sensor.get_distance()/10 #cm
        if measurement<819: #object within range
            distance += measurement
            count +=1
    
    if nSamples-count>nSamples//2:
        distance = 819
    else:
        distance /= count

    #Format output string
    data = "light="+str(lux)+","
    data +="distance="+str(distance)

    print(colored(" Light:","blue"), lux, colored("Distance:","blue"), distance)
    return data
##################################################
def send_data(data):

    prom = Prometheus()
    prom.put(data)
    return
##################################################
def test_module():            
            
    if __name__ == '__main__':
        data = collect_data()
        send_data(data)
#############################################
test_module()
#############################################