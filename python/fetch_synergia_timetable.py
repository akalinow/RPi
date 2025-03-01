#!/bin/python3

import requests
import json
from datetime import datetime, timedelta
    
from librus_apix.schedule import get_schedule, schedule_detail    
from librus_apix.timetable import get_timetable, Period


#############################################
def test0():
    login = "11852563"
    password = "Pi=3.1415"
    API_URL = "https://api.librus.pl/"

    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT x.y; Win64; x64; rv:10.0) Gecko/20100101 Firefox/10.0",
    "Content-Type": "application/x-www-form-urlencoded",
    }

    proxy = {}


    response = requests.get(API_URL
                + "/OAuth/Authorization?client_id=46&response_type=code&scope=mydata",
                headers=headers,
                proxies=proxy,
            )

    response = requests.post(
                API_URL + "/OAuth/Authorization?client_id=46",
                data={"action": "login", "login": login, "pass": password},
                headers=headers,
                proxies=proxy,
                cookies=response.cookies,
            )
    print(response.cookies)
#############################################
def period_json(period: Period, events: dict):


    event = ""
    if period.date in events.keys() and period.subject in events[period.date].keys():
        event = events[period.date][period.subject]

    return {
            "date": period.date,
            "date_from": period.date_from,
            "date_to": period.date_to,
            "weekday": period.weekday,
            "subject": period.subject,
            "teacher_and_classroom": period.teacher_and_classroom,
            "event": event
        }
#############################################   
def getScheduleJSON():

    from librus_apix.client import Client, Token, new_client
    from librus_apix.grades import get_grades

    
    # create a new client with empty Token()
    client: Client = new_client()
    # update the token
    login = "11852563"
    password = "Pi=3.1415"
    _token: Token = client.get_token(login, password)
    # now you can pass your client to librus-apix functions
    
    key = client.token.API_Key
    print(key)
    
    #key = 'L30~e67cd7c2267e76942d8f92bb2a5fec15:e67cd7c2267e76942d8f92bb2a5fec15'

    # you can store this key and later load it in ways like this:
    ## Load directly into token object
    token = Token(API_Key=key)
    client: Client = new_client(token=token)
    ## or put it into existing client
    client.token = token
    ## or into empty token
    client.token.API_Key = key
    
    month = datetime.now().month
    year =  datetime.now().year
    schedule = get_schedule(client, month, year)
    
    events = {}
    for day in schedule:
        for event in schedule[day]:
            if event.href.find('/')==-1:
                continue
            
            prefix, href = event.href.split('/')
            details = schedule_detail(client, prefix, href)

            if "Przedmiot" in details.keys() and "Data" in details.keys() and "Rodzaj" in details.keys():

                if details["Data"] not in events:
                    events[details["Data"]] = {}
                events[details["Data"]][details["Przedmiot"]] = details["Rodzaj"]
            else:
                print(details) 

    print(events)               
                 
    monday_datetime = datetime.now()-timedelta(days=datetime.now().weekday())
    if datetime.now().weekday()>=5:
        monday_datetime = monday_datetime + timedelta(days=7)

    timetable = get_timetable(client, monday_datetime)

    print("Monday: ", monday_datetime)

    timetable_map = {}
    weekday_list = []
    for weekday in timetable:
        for period in weekday:
            if not period.subject:
                continue
            weekday_list.append(period_json(period, events))
        timetable_map[period.weekday] = weekday_list
        weekday_list = []
     
    fileName = './timetable.json'
    with open(fileName, 'w', encoding='utf-8') as file:
        json.dump(timetable_map, file, indent=4, ensure_ascii=False)

#############################################
getScheduleJSON()
