#!/bin/python3

import datetime, json
import pandas as pd
import numpy as np
import glob

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
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

    ax = fig.add_subplot(gs[0,0])
    addTimeTable(ax, "timetable.json")    
    addInfoBox(ax)

    ax = fig.add_subplot(gs[0,1:])
    addAnnotations(ax)
    addEnvData(ax, "sensor_data.csv", "ICM_data.csv")

    ax = fig.add_subplot(gs[1,1:])
    addAnnotations(ax, addDates=False)
    addCO2Data(ax, "sensor_data.csv")
    
    plt.subplots_adjust(right=0.85, left=0.1, top=0.95, bottom=0.1, hspace=0.5)
    plt.show()
    plt.savefig('./temperature.jpg', dpi=100)
################################################
################################################
def addInfoBox(axis):
    
    #Add info box
    text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    stylename = "round4, pad=0.5"
    axis.text(0.6,0.9,
              text, bbox=dict(boxstyle=stylename, fc="w", ec="k"),
              transform=axis.transAxes, size="large", color="blue",
              horizontalalignment="right", verticalalignment="center")

################################################
################################################
def addAnnotations(axis, addDates=True):

    axis.xaxis.axis_date(tz='Europe/Warsaw')

    #Annotate dates
    if addDates:
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

    xmin = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    xmax = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=2))
    axis.set_xlim(xmin, xmax)
 
    axis.xaxis.set_major_locator(mdates.HourLocator(interval=6))
    axis.xaxis.set_major_formatter(mdates.DateFormatter('%H'))
    axis.set_xticks(axis.get_xticks(), axis.get_xticklabels(), rotation=45)

    return axis
################################################
################################################
def addEnvData(axis, csvSensorFile, csvForecastFile):

    #Load data
    df = loadPandas(csvSensorFile)
    df_forecast = loadPandas(csvForecastFile)
    if df.empty:
        return
    
    #Plot temperature
    axis.plot_date(df_forecast['Date'], df_forecast["Temperature"]-273.15, label='ICM', color='black', fmt=".")
    axis.plot_date(df['Date'], df["Temperature_K"], label='Salon', color='red', fmt=".")
    axis.plot_date(df['Date'], df["Temperature_Solar"], label='Balkon', color='green', fmt=".")

    #Plot fall
    ax2 = axis.twinx()  
    color = 'blue'
    ax2.set_ylabel('Opad [mm/h]', color=color)
    ax2.fill_between(df_forecast['Date'],0.0, df_forecast['Fall'], alpha=0.7)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 5)

    #Adapt axes
    axis.set(xlabel='', ylabel=r'Temp. $[^{\circ}$C]',title='')

    yMin, yMax = axis.get_ylim()
    axis.set_ylim(yMin-2, yMax+2)
    
    #Add labels
    df_tmp = df[['Date', 'Temperature_K']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_K"].iloc[-1])
    axis.annotate("Salon:\n"+str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.83,0.58),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='red',
                  arrowprops=dict(arrowstyle="->"))
    
    df_tmp = df[['Date', 'Temperature_Solar']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_Solar"].iloc[-1])
    axis.annotate("Balkon:\n"+str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(1.05, -0.75),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='green',
                  arrowprops=dict(arrowstyle="->"))
    
################################################
################################################
def addCO2Data(axis, csvSensorFile):

    #Load data
    df = loadPandas(csvSensorFile)
    if df.empty:
        return
    
    axis.plot_date(df['Date'], df["CO2_K"], label='Salon', color='red', fmt=".")

    #Adapt axes
    axis.set(xlabel='', ylabel=r'CO$_{2}$ [ppm]',title='')
    axis.set_ylim(300, 3000)

    #Add labels
    df_tmp = df[['Date', 'CO2_K']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["CO2_K"].iloc[-1])
    axis.annotate("Salon:\n"+str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.8,0.58),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='red',
                  arrowprops=dict(arrowstyle="->"))
    
    #draw horizontal line at 350 (background level)
    axis.axhline(350, color='black', linewidth=2, linestyle='--')

################################################
################################################
def addTimeTable(axis, json_file):

    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            timetable_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{json_file}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{json_file}'.")
        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    all_lessons = []
    for day in days:
        for lesson in timetable_data.get(day, []):
            all_lessons.append(lesson)

    df = pd.DataFrame(all_lessons)

    if df.empty:
        print("No data to plot.")
        return

    # Convert time strings to datetime.time objects
    df['date_from'] = pd.to_datetime(df['date_from'], format='%H:%M').dt.time
    df['date_to'] = pd.to_datetime(df['date_to'], format='%H:%M').dt.time

    print(df)
    return

    # Define a color palette for subjects
    subjects = df['subject'].unique()
    num_subjects = len(subjects)
    colors = plt.get_cmap('tab20', num_subjects)  # Use a qualitative colormap

    subject_colors = {subject: colors(i) for i, subject in enumerate(subjects)}

    # Set y-axis (days)
    day_indices = range(len(days))
    plt.yticks(day_indices, days)
    axis.invert_yaxis()  # Put Monday at the top

    # Set x-axis (time)
    start_time = min(df['date_from'])
    end_time = max(df['date_to'])
    time_delta = 0.15 #(pd.to_datetime(end_time) - pd.to_datetime(start_time)).total_seconds() / 3600

    print(f"Start time: {start_time}, End time: {end_time}")
    return

    start_time_dt = pd.to_datetime(start_time)
    end_time_dt = pd.to_datetime(end_time)

    #Dynamically set the x ticks.  Much cleaner and avoids hardcoding
    num_ticks = 10  # Adjust the number of ticks as needed
    time_interval = time_delta / num_ticks
    xticks = [start_time_dt + pd.Timedelta(hours=i * time_interval) for i in range(num_ticks + 1)]
    xticklabels = [t.strftime('%H:%M') for t in xticks]  # Format as HH:MM

    plt.xticks(xticks, xticklabels, rotation=45, ha='right')
    axis.set_xlim(start_time_dt, end_time_dt) #Sets x axis limits with datetime

    # Plot the lessons
    for index, row in df.iterrows():
        day_index = days.index(row['weekday'])
        start = pd.to_datetime(row['date_from'])
        end = pd.to_datetime(row['date_to'])
        duration = (end - start).total_seconds() / 3600

        # Plot rectangle for the lesson
        axis.barh(day_index, width = duration, left = start, height=0.8, color=subject_colors[row['subject']], align='center')

        # Add subject label
        axis.text(start + pd.Timedelta(hours=duration/2), day_index, row['subject'], ha='center', va='center', color='white', fontsize=9)


    # Add Legend
    handles = [plt.Rectangle((0,0),1,1, color=subject_colors[subject]) for subject in subjects]
    axis.legend(handles, subjects, loc='upper left', bbox_to_anchor=(1, 1))

    # Add title and labels
    axis.title('Timetable')
    axis.xlabel('Time')
    axis.ylabel('Day')
#############################################
#############################################
def test_module():            
            
    if __name__ == '__main__':
        makePlots()
#############################################
test_module()
