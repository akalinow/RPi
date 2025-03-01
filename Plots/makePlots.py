#!/bin/python3

import datetime
import pandas as pd
import numpy as np
import glob

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import (AnnotationBbox, DrawingArea, OffsetImage,
                                  TextArea)
from matplotlib.patches import Circle

#set xkcd style
#plt.xkcd()

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
    params = {'legend.fontsize': 'x-large',
          'figure.figsize': (5,5),
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
    plt.rcParams.update(params)

    fig = plt.figure(figsize=(8.0, 4.8)) 
    gs = GridSpec(3, 3, figure=fig)
    ax = fig.add_subplot(gs[0,1:])
    addEnvData(ax)
    
    plt.show()
    plt.savefig('temperature.png')
################################################
################################################
def addEnvData(axis):

    #Load data
    df = loadPandas("../EnvData/sensor_data.csv")
    df_forecast = loadPandas("../EnvData/ICM_data.csv")
    if df.empty:
        return
    
    axis.xaxis.axis_date(tz='Europe/Warsaw')
    #Plot temperature
    axis.plot_date(df_forecast['Date'], df_forecast["Temperature"]-273.15, label='ICM', color='black', linewidth=1)
    axis.plot_date(df['Date'], df["Temperature_K"], label='Salon', color='red', linewidth=3)
    axis.plot_date(df['Date'], df["Temperature_Solar"], label='Balkon', color='green', linewidth=3)

    #Plot fall
    ax2 = axis.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('Opad [mm/h]', color=color)
    ax2.fill_between(df_forecast['Date'],0.0, df_forecast['Fall'], alpha=0.7)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 5)

    ##Add annotations
    #da = DrawingArea(20, 20, 0, 0)
    #p = Circle((10, 10), 10)
    #da.add_artist(p)
    da = TextArea("Salon", textprops=dict(color="red", size=20, rotation=0))

    
    '''
    xy = (0.5, 0.5)
    ab = AnnotationBbox(da, xy,
                    xybox=(0.05, 0.75),
                    xycoords='axes fraction',
                    boxcoords=("axes fraction"),
                    box_alignment=(0.1, 0.1),
                    arrowprops=dict(arrowstyle="->"),
                    bboxprops=dict(alpha=0.5))
    axis.add_artist(ab)
    '''

    #Adapt axes
    axis.set(xlabel='', ylabel=r'Temp. $[^{\circ}$C]',title='')

    yMin, yMax = axis.get_ylim()
    axis.set_ylim(yMin-2, yMax+2)
    
    xmin = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    xmax = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=2))
    axis.set_xlim(xmin, xmax)
 
    axis.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    
    #Annotate dates
    axis.annotate((datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.01, 1.05), 
                xycoords='axes fraction', fontsize=15, color='black')
    
    axis.annotate(datetime.datetime.now().strftime('%Y-%m-%d'), xy=(0.36, 1.05), 
                xycoords='axes fraction', fontsize=15, color='black')
    
    axis.annotate((datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.70, 1.05), 
                xycoords='axes fraction', fontsize=15, color='black')
    
    #draw vertical line at current time
    x1 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    x2 = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    axis.axvline(x1, color='black', linewidth=2, linestyle=':')
    axis.axvline(x2, color='black', linewidth=2, linestyle=':')
    
    #draw horizontal line at 0
    axis.axhline(0, color='black', linewidth=2, linestyle='--')

    #Add labels
    print(df)
    df_tmp = df[['Date', 'Temperature_K']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_K"].iloc[-1])
    axis.annotate("Salon:"+str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.02, 0.78),
                  textcoords='axes fraction', 
                  fontsize=20, 
                  color='red',
                  arrowprops=dict(arrowstyle="->"))
    
    df_tmp = df[['Date', 'Temperature_Solar']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_Solar"].iloc[-1])
    axis.annotate("Balkon:"+str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.02, 0.50),
                  textcoords='axes fraction', 
                  fontsize=20, 
                  color='green',
                  arrowprops=dict(arrowstyle="->"))
    
    #adjust margins
    #plt.subplots_adjust(right=0.95, left=0.12, top=0.85, bottom=0.14)
    axis.set_xticks(axis.get_xticks(), axis.get_xticklabels(), rotation=90)
    #axis.legend()

################################################
################################################
def test_module():            
            
    if __name__ == '__main__':
        makePlots()
#############################################
test_module()
