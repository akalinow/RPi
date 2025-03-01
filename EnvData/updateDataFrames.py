#!/bin/python3

import gc
import requests, json, datetime
import pandas as pd
import numpy as np
import glob

################################################
################################################
def fetch_prom_data(query):

    from secrets_ak import PROM_URL, PROM_USER_ID, PROM_API_KEY

    query = PROM_URL + '?query=' + query

    try: 
        response = requests.get(url=query,
                                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                auth = (PROM_USER_ID, PROM_API_KEY)
        )
    except OSError as e:
        print(e)
        return {}
            
    status_code = response.status_code
    if status_code != 200:
        print('Error:', status_code)
        return {}

    json_data = json.loads(response.text)
    if not len(json_data['data']['result']):
               return
    #print(json_data)

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
        df = pd.read_csv(pd_path, parse_dates=["Date"])
        df.index.rename('Date', inplace=True)
        df.index = pd.to_datetime(df["Date"])
        df.drop(columns=["Date"], inplace=True)

    measurements = ["Temperature", "CO2"]
    for aMeasurement in measurements:
        data = fetch_prom_data("env_data_"+aMeasurement+"[2h]")
        fileName = './sensor_data_'+aMeasurement+'.json'
        with open(fileName, 'w') as f:
            json.dump(data, f)
        ##append df
        df_tmp = pd.read_json(fileName, convert_dates="Date", orient='records')
        df_tmp.index.rename('Date', inplace=True)

        df = pd.concat([df, df_tmp], axis=0, join='outer')
        df.drop_duplicates(inplace=True)
        
    df.to_csv(pd_path)
##################################################
##################################################
def updateForecastPandas():
     
    pd_path = "./ICM_data.csv" 
    dataPath = "../ICM/"
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
