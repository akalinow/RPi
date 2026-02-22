#!/bin/python3

import json, datetime
import pandas as pd
import numpy as np
import glob
from Prometheus import Prometheus

################################################
################################################
def fetch_prom_data(query):

    prom = Prometheus()
    data = prom.get(query)
    if data is None:
        return {}

    json_data = json.loads(data)
    if not len(json_data['data']['result']):
               return

    data = {}
    for result in json_data['data']['result']:
        lastValue = result['values'][-1]
        timestamp = int(lastValue[0])
        timestamp = datetime.datetime.fromtimestamp(timestamp).astimezone().isoformat()
        value = lastValue[1]
        tag = query.split('_')[-1].split('[')[0]   +"_"+result['metric']['bar_label']
        data[tag] = {timestamp:value}
        print('Tag:\t', tag,'\t', timestamp, 'Value:', value)

    return data 
################################################
################################################
def updateMeasurementPandas():

    pd_path = "./sensor_data.csv"
    df = pd.DataFrame()
    if glob.glob(pd_path):
        df = pd.read_csv(pd_path, parse_dates=["Date"], date_format='mixed')
        df.index.rename('Date', inplace=True)
        df.index = pd.to_datetime(df["Date"], utc=True)
        df.drop(columns=["Date"], inplace=True)

    measurements = ["env_data_Temperature[2h]", "env_data_CO2[2h]", 
                    "RPi_id[2h]", "RPi_fraction[2h]", 
                    "balkon_distance_sonic[2h]",  "balkon_distance_tof[2h]",
                    "env_data_pm1_0[2h]","env_data_pm2_5[2h]","env_data_pm10[2h]"
                    ] 
    for aMeasurement in measurements:
        data = fetch_prom_data(aMeasurement)
        fileName = './sensor_data_'+aMeasurement+'.json'
        with open(fileName, 'w') as f:
            json.dump(data, f) 
        ##append df
        df_tmp = pd.read_json(fileName, convert_dates="Date", orient='records')
        df_tmp.index.rename('Date', inplace=True)
        df_tmp.index = pd.to_datetime(df_tmp.index, utc=True)
        df = pd.concat([df, df_tmp], axis=0, join='outer')
        #df.drop_duplicates(inplace=True)
        
    #print(df)  
    df.to_csv(pd_path)
##################################################
##################################################
def updateForecastPandas():
     
    pd_path = "./ICM_data.csv" 
    dataPath = "./"
    dataDict = {"Temperature": "forecast_data_03236_0000000.json",
                "Fall": "forecast_data_05226M0001500.json"
    }
    
    df = pd.DataFrame()

    for aMeasurement in dataDict.keys():
        filePath = dataPath + dataDict[aMeasurement]
        if glob.glob(filePath):
            ##read json
            data = json.load(open(filePath))
            data = list(data.values())[0]
            df_tmp = pd.DataFrame(data["data"], index = data["times"], columns=[aMeasurement])
            df = pd.concat([df, df_tmp], axis=0)   
            #df.drop_duplicates(inplace=True)

    df.index.rename('Date', inplace=True)
    df.to_csv(pd_path, index=True)
##################################################
##################################################
def test_module():            
            
    if __name__ == '__main__':
        updateMeasurementPandas()     
        updateForecastPandas()
#############################################
test_module()
