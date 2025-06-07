#!/bin/python3

import datetime, json
import pandas as pd
import numpy as np
import glob
from zoneinfo import ZoneInfo

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import (AnnotationBbox, DrawingArea, OffsetImage,
                                  TextArea)
import matplotlib.transforms as mtransforms
from matplotlib.patches import Circle, FancyBboxPatch

import locale
locale.setlocale(locale.LC_ALL, 'pl_PL.UTF-8')

#set xkcd style
#plt.xkcd()

################################################
################################################
def loadPandas(cvsFile):
    pd_path = cvsFile
    df = pd.DataFrame()
    if glob.glob(pd_path):
        df = pd.read_csv(pd_path, parse_dates=['Date'], date_format="ISO8601")
        df["Date"] = pd.to_datetime(df["Date"], utc=True)
    return df
################################################
################################################
def loadTimeTablePandas(jsonFile):

    timetable_data = {}
    try:
        with open(jsonFile, 'r', encoding='utf-8') as f:
            timetable_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: File '{jsonFile}' not found.")
        return
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in '{jsonFile}'.")
        return

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    all_lessons = []
    for day in days:
        for lesson in timetable_data.get(day, []):
            all_lessons.append(lesson)

    df = pd.DataFrame(all_lessons)
    # Convert time strings to datetime.time objects
    df['date_from'] = pd.to_datetime(df['date_from'], format='%H:%M').dt.time
    df['date_to'] = pd.to_datetime(df['date_to'], format='%H:%M').dt.time

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
         'ytick.labelsize':'x-large',
         'timezone':'Europe/Warsaw'}
    plt.rcParams.update(params)

    fig = plt.figure(figsize=(8.0, 4.4)) 
    gs = GridSpec(3, 3, figure=fig)

    ax = fig.add_subplot(gs[:,0])
    date = datetime.datetime.now()
    if date.hour > 12:
        date = date + datetime.timedelta(days=1)
    elif date.weekday() > 4:
        date = date + datetime.timedelta(days=7-date.weekday())  

    addTimeTable(ax, "timetable.json", date)    
    addInfoBox(ax)

    ax = fig.add_subplot(gs[0,1:])
    addAnnotations(ax)
    addEnvData(ax, "sensor_data.csv", "ICM_data.csv")

    ax = fig.add_subplot(gs[1,1:])
    addAnnotations(ax, addDates=False)
    addCO2Data(ax, "sensor_data.csv")

    ax = fig.add_subplot(gs[2,1:])
    addAnnotations(ax, addDates=False)
    addPresenceData(ax, "sensor_data.csv", id=0, label="AK", color="red")
    addPresenceData(ax, "sensor_data.csv", id=1, label="WK", color="green")
    
    plt.subplots_adjust(right=0.88, left=0.0, top=0.95, bottom=0.1, hspace=0.5, wspace=0.4)
    plt.savefig('./temperature.jpg', dpi=100)
    #plt.show()
################################################
################################################
def addInfoBox(axis):
    
    #Add info box
    text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    text = "Aktualizacja: "+text
    stylename = "round4, pad=0.5"
    axis.text(0.05, 1.03,
              text, bbox=dict(boxstyle=stylename, fc="w", ec="k"),
              transform=axis.transAxes, size=8, color="blue",
              horizontalalignment="left", verticalalignment="center")

################################################
################################################
def addAnnotations(axis, addDates=True):

    #axis.xaxis.axis_date(tz='Europe/Warsaw')

    #Annotate dates
    if addDates:
        axis.annotate((datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.01, 1.05), 
                    xycoords='axes fraction', fontsize=15, color='black')
        
        axis.annotate(datetime.datetime.now().strftime('%Y-%m-%d'), xy=(0.36, 1.05), 
                    xycoords='axes fraction', fontsize=15, color='black')
        
        axis.annotate((datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d'), xy=(0.70, 1.05), 
                    xycoords='axes fraction', fontsize=15, color='black')
    
    #draw vertical line at current time
    tzinfo = ZoneInfo("Europe/Warsaw")
    x1 = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    x2 = (datetime.datetime.now() + datetime.timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    x1 = x1.astimezone(tzinfo)
    x2 = x2.astimezone(tzinfo)
    axis.axvline(x1, color='black', linewidth=2, linestyle=':')
    axis.axvline(x2, color='black', linewidth=2, linestyle=':')
    
    #draw horizontal line at 0
    axis.axhline(0, color='black', linewidth=2, linestyle='--')

    xmin = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    xmax = (datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=2))

    xmin = xmin.astimezone(tzinfo)
    xmax = xmax.astimezone(tzinfo)
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

    #Plot fall
    ax2 = axis.twinx()  
    color = 'navy'
    ax2.set_ylabel('Opad [mm/h]', color=color)
    ax2.fill_between(df_forecast['Date'],0.0, df_forecast['Fall']*4.0) #rainfall given kg/m2/15 min convert to kg/m2/h 
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(0, 5)
      
    #Plot temperature   
    axis.plot_date(df_forecast['Date'], df_forecast["Temperature"]-273.15, label='ICM', color='black', fmt=".")
    axis.plot_date(df['Date'], df["Temperature_K"], label='Salon', color='red', fmt=".")
    axis.plot_date(df['Date'], df["Temperature_Solar"], label='Balkon', color='green', fmt=".")

    #Adapt axes
    axis.set(xlabel='', ylabel=r'Temp. $[^{\circ}$C]',title='')

    yMin, yMax = axis.get_ylim()
    axis.set_ylim(yMin-2, yMax+2)
    axis.set_ylim(5, 35)
    axis.yaxis.set_major_locator(plt.MultipleLocator(5))

    #Add labels
    df_tmp = df[['Date', 'Temperature_K']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_K"].iloc[-1])
    axis.annotate(str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.83,0.70),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='red',
                  weight='bold',
                  bbox=dict(boxstyle="round,pad=0.3",
                      fc="lightblue", ec="steelblue", lw=2),
                  arrowprops=dict(arrowstyle="->"))
    
    df_tmp = df[['Date', 'Temperature_Solar']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["Temperature_Solar"].iloc[-1])
    axis.annotate(str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.83, 0.20),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='green',
                  weight='bold',
                  bbox=dict(boxstyle="round,pad=0.3",
                      fc="lightblue", ec="steelblue", lw=2),
                  arrowprops=dict(arrowstyle="->"))

    axis.legend(bbox_to_anchor=(1.01, -0.3),
                loc='upper left', borderaxespad=0.,
                markerfirst=False,
                labelcolor="linecolor",
                frameon=False,
                alignment="left",
                prop={"weight":"bold"})
    
################################################
################################################
def addCO2Data(axis, csvSensorFile):

    #Load data
    df = loadPandas(csvSensorFile)
    if df.empty:
        return
    
    axis.plot_date(df['Date'], df["CO2_K"], label='Salon', color='red', fmt=".")

    #Adapt axes
    axis.set(xlabel='', ylabel=r'CO$_{2}$ [ppk]',title='')
    axis.set_ylim(200, 3000)

    #Add labels
    df_tmp = df[['Date', 'CO2_K']].copy()
    df_tmp = df_tmp.dropna()
    xy = (df_tmp["Date"].iloc[-1], df_tmp["CO2_K"].iloc[-1])
    axis.annotate(str(xy[1]),
                  xy=xy,
                  xycoords='data',
                  xytext=(0.8,0.70),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color='red',
                  weight='bold',
                  bbox=dict(boxstyle="round,pad=0.3",
                  fc="lightblue", ec="steelblue", lw=2),
                  arrowprops=dict(arrowstyle="->"))
    
    yticks = np.arange(200, 3000, 500)
    ylabels = [f'{y/1000:1.1f}' for y in yticks]
    axis.set_yticks(yticks, labels=ylabels)
    #draw horizontal line at 350 (background level)
    axis.axhline(350, color='black', linewidth=2, linestyle='--')

################################################
################################################
def addPresenceData(axis, csvSensorFile, id, label, color):

    #Load data
    df = loadPandas(csvSensorFile)
    if df.empty:
        return

    #Merge id and presence fraction rows
    agg_id = pd.NamedAgg(column="id_RPi", aggfunc="min")
    agg_fraction = pd.NamedAgg(column="fraction_RPi", aggfunc="min")
    df_merged = df.groupby(df["Date"]).agg(id_RPi=agg_id, fraction_RPi=agg_fraction)
    df_merged.dropna(how='any', inplace=True)
    df = df_merged
    df["Date"] = df.index

    #Select person
    mask = (df["id_RPi"]==id)

    #Plot
    x = df["Date"][mask]
    y = (df["id_RPi"][mask]==id)
    axis.plot_date(x, y, label=label, color=color, fmt=".")
    #axis.plot(x, y, label=label, color=color)
   
    #Adapt axes
    axis.set(xlabel='', ylabel=r'Presence',title='')
    axis.set_ylim(0, 1.1)

    xmin = datetime.datetime.now().replace(hour=21, minute=0, second=0, microsecond=0) - datetime.timedelta(days=1)
    xmax = (datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1))
    axis.set_xlim(xmin, xmax)

    yticks = np.arange(0, 1.1, 1.0)
    ylabels = [yTicks for yTicks in yticks]
    axis.set_yticks(yticks, labels=ylabels)

    #Count presence time during current day
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    midnight = pd.to_datetime(midnight, utc=True)
    mask *= (df['Date']>=midnight) 
    y = (df["id_RPi"][mask]==id)*df["fraction_RPi"][mask]
 
    #Single count corresponds to 10'
    countsToSeconds = 600.0
    count = np.sum(y)
    if count<1:
        return
        
    time = str(datetime.timedelta(seconds=count*countsToSeconds)).split(":")[:-1]
    time = label+" "+":".join(time)
    
    #Add labels
    df_tmp = df[['Date', 'id_RPi']].copy()
    
    xy = (df_tmp["Date"].iloc[-1], df_tmp["id_RPi"][mask].iloc[-1])
    axis.annotate(time,
                  xy=xy,
                  xycoords='data',
                  xytext=(0.75,0.70-id*0.5),
                  textcoords='axes fraction', 
                  fontsize=15, 
                  color=color,
                  weight='bold',
                  bbox=dict(boxstyle="round,pad=0.3",
                  fc="lightblue", ec="steelblue", lw=2),
                  arrowprops=dict(arrowstyle="->", color="white"))

       
################################################
################################################
def addTimeTable(axis, json_file, date):

    #Hide axes
    axis.axis('off')

    textWidthChars = 15
    rowHeight = 0.13
    boxSizeAxisFraction = np.array((0.9, 0.02))
    boxXYAxisFraction = np.array((0.04, 0.85))
    stylename = "round4, pad=0.5"
    bboxParams=dict(boxstyle=stylename, facecolor="yellow", ec="k", lw=2)

    df = loadTimeTablePandas(json_file)

    #Filter data on date
    df = df.loc[df["date"]==date.strftime('%Y-%m-%d')]

    #Add weekday name
    text = date.strftime('%A').capitalize()
    bbox = axis.text(0.5, 0.95,
              text, bbox=bboxParams,
              transform=axis.transAxes, size=15, color="black",
              horizontalalignment="center", verticalalignment="center")

    for index in range(len(df)):
        item = df.iloc[index]

        rowHeight = 0.13
        boxSizeAxisFraction = np.array((0.9, 0.02))
        
        #start/end time
        text = "$^{"+item["date_from"].strftime('%H:%M')+"}"
        text += "_{"+item["date_to"].strftime('%H:%M')+"}$"
        #subject
        subject = item["subject"].strip('język')
        if subject == "godzina wychowawcza":
            subject = "godz. wych."
        elif subject == "wychowanie fizyczne":
            subject = "WF"
        elif "native" in subject:
            subject = "ang. - NS" 
       
        text += subject
        #event 
        eventText = item['event'].capitalize() 
        if item['event']:
            text += "\n"
            fc = "red"
            textColor = "white"
        else:
            fc = "yellow"
            textColor = "black"
    
        #Latex formatting             
        text = r"{}".format(text)

        #bbox plotting
        bb = mtransforms.Bbox([boxXYAxisFraction, boxXYAxisFraction+boxSizeAxisFraction])
        fancy = FancyBboxPatch(bb.p0, bb.width, bb.height, boxstyle="round,pad=0.05", fc=fc, ec="k", lw=2)
        axis.add_patch(fancy)

        bbox = axis.text(*(boxXYAxisFraction + np.array((-0.03, 0))),
                text, 
                size=15, color=textColor,
                horizontalalignment="left", 
                verticalalignment="center")  
        
        if eventText:
            bbox = axis.text(*(boxXYAxisFraction + np.array((0.25, -0.025))),
                eventText.upper(),
                size=12, color=textColor,
                horizontalalignment="left", 
                verticalalignment="center")

        boxXYAxisFraction += np.array((0,-rowHeight))  
        #break

    # hide axes
    #axis.axis('off')
    return

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
