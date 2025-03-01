#!/bin/python3

import datetime
import pandas as pd
import numpy as np
import glob

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

################################################
################################################
def loadPandas(cvsFile):
    pd_path = cvsFile
    df = pd.DataFrame()
    if glob.glob(pd_path):
        df = pd.read_csv(pd_path, parse_dates=['Date'], date_format="ISO8601")
    return df
################################################
################################################
def makePlots():

    #Increase labels and font size
    params = {'legend.fontsize': 'xx-large',
          'figure.figsize': (10, 7),
         'axes.labelsize': 'xx-large',
         'axes.titlesize':'xx-large',
         'xtick.labelsize':'xx-large',
         'ytick.labelsize':'xx-large'}
    plt.rcParams.update(params)

    #Load data
    df = loadPandas("sensor_data.csv")
    df_forecast = loadPandas("ICM_data.csv")
    if df.empty:
        return
        
    fig, ax = plt.subplots(figsize=(7, 3))

    ax.xaxis.axis_date(tz='Europe/Warsaw')
    #Plot lines
    print(df)
    ax.plot_date(df_forecast['Date'], df_forecast["Temperature"]-273.15, label='ICM', color='black', linewidth=1)
    ax.plot_date(df['Date'], df["Temperature_K"], label='Salon', color='red', linewidth=3)
    #ax.plot_date(df['Date'], df["Temperature_Solar"], label='Balkon', color='green', linewidth=3)
    
    #Adapt axes
    ax.set(xlabel='', ylabel=r'Temp. $[^{\circ}$C]',title='')
    
    xmin = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    xmax = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=2))
    ax.set_xlim(xmin, xmax)
 
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    
    #Annotate dates
    ax.annotate((datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.01, 1.05), 
                xycoords='axes fraction', fontsize=20, color='black')
    
    ax.annotate(datetime.datetime.now().strftime('%Y-%m-%d'), xy=(0.36, 1.05), 
                xycoords='axes fraction', fontsize=20, color='black')
    
    ax.annotate((datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.70, 1.05), 
                xycoords='axes fraction', fontsize=20, color='black')
    
    #draw vertical line at current time
    x1 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    x2 = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    ax.axvline(x1, color='black', linewidth=2, linestyle=':')
    ax.axvline(x2, color='black', linewidth=2, linestyle=':')
    
    #draw horizontal line at 0
    ax.axhline(0, color='black', linewidth=2, linestyle='--')
    
    #adjust margins
    plt.subplots_adjust(right=0.95, left=0.12, top=0.85, bottom=0.14)
    
    plt.xticks(rotation=90)
    plt.legend()
    plt.show()
    plt.savefig('temperature.png')

################################################
################################################
def test_module():            
            
    if __name__ == '__main__':
        makePlots()
#############################################
test_module()
