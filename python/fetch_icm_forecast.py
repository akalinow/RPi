#!/bin/python3

import requests
import json
import time

################################################
# Fetch data from ICM
def fetch_ICM_data(coords, field, date):
   
    from secrets_ak import ICM_URL, ICM_API_KEY
    
    url = ICM_URL.format(coords, field, date)
    print("ICM url:",url)
 
    response = requests.post(ICM_URL.format(coords, field, date),
                            headers = {'Authorization': 'Token {}'.format(ICM_API_KEY) }, 
                          )

    status_code = response.status_code
    if status_code != 200:
        print('Error:', status_code)
        return -1

    data = {}
    data[field] = json.loads(response.text)
    json_data = json.dumps(data)
    
    fileName = './forecast_data_'+field+'.json'
    with open(fileName, 'w') as f:
        json.dump(data, f)
    return 0    
################################################
def getWarsawData(timestamp, field):
    ##Warsaw
    #coords = '266,332'# Warsaw WRF
    coords = '212,252' # Warsaw UM grid: P5
    #coords = '284,386' #WRF Test point, free of charge
    date = "{:04d}-{:02d}-{:02d}T00".format(*timestamp)
    return fetch_ICM_data(coords, field, date)
################################################
def updateForecastField(timestamp, field, lastStatus):
    return getWarsawData(timestamp, field)
################################################
def updateForecast(timestamp, lastStatus):
    #WRF
    #result = updateForecastField(timestamp, "T2", lastStatus)
    #result = updateForecastField(timestamp, "RAINNC", lastStatus)
    
    #UM
    result = updateForecastField(timestamp, "03236_0000000", lastStatus)
    result = updateForecastField(timestamp, "05226M0001500", lastStatus)    
    return result
################################################
def test_module():            
            
    if __name__ == '__main__': 
        timestamp = time.localtime()

        lastStatus = -1
        lastStatus = updateForecast(timestamp, lastStatus)
        print(lastStatus)
################################################
test_module()





