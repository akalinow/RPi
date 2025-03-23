#!/bin/python3

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
    tof_sensor.start_ranging(VL53L0X.Vl53l0xAccuracyMode.LONG_RANGE)

    # Create light sensor
    light_sensor = TSL2591.TSL2591()

    lux = light_sensor.Lux
    distance = tof_sensor.get_distance()/10 #cm

    print(colored(" Light:","blue"), lux, colored("Distance:","blue"), distance)
##################################################
def send_data(data):

    prom = Prometheus()
    prom.put(data)
    return
##################################################
def test_module():            
            
    if __name__ == '__main__':
        data = collect_data()
        #send_data(data)
#############################################
test_module()
#############################################