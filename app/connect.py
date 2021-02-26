from icalendar import Calendar as iCalendar, vDatetime
import calendar
import enum
import os
from dateutil.relativedelta import relativedelta
from dateutil.rrule import *
from dateutil.parser import *
#from app import db
#from app.models import Calendars, Connections
#from app.utils import get_block_view
import requests
import datetime




# To avoid ambiguity, day is defined as a number whilst weekday represents a day of the week

section_string = {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Placeholder Text"
                    }
		         }

frequencies = {"WEEKLY" : WEEKLY, "HOURLY" : HOURLY, "MINUTELY" : MINUTELY, "DAILY" : DAILY, "MONTHLY" : MONTHLY, "YEARLY" : YEARLY, "SECONDLY" : SECONDLY}
weekdays = {'MO' : 0, 'TU' : 1, 'WE' : 2, 'TH' : 3, 'FR' : 4, 'SA' : 5, 'SU' : 6} 

calendar = iCalendar.from_ical(requests.get("https://my.unsw.edu.au/cal/pttd/DhqByKyFvK.ics").text)

for component in calendar.walk():
    if component.name == 'VEVENT' and 'RRULE' in component.keys():
        rule = component.get('RRULE')
        datetime= rule['UNTIL'][0]
        print(list(rrule(freq=WEEKLY, until=datetime, byweekday=weekdays[rule['BYDAY'][0]])))

def add(user_id, url):
    http_url = url.replace('webcal', 'https')
    calendar = iCalendar.from_ical(requests.get(http_url).text)
    db.session.add(Calendars(user_id=user_id, calendar=calendar))



def connect(connector, connectee):
    # Query Connections database for connector
    connector_instance = db.session.query(Connections).get(connector)
    connectee_instance = db.session.query(Connections).get(connector)

    if db.session.query(Calendars).get(connector) is None or db.session.query(Calendars).get(connectee) is None:
        return False


    # If connector doesn't exist, add a new connection
    if connector_instance is None:
        db.session.add(Connections(user_id=connector, connections = connectee))
        db.session.commit() 

    if connectee_instance is None:
        db.session.add(Connections(user_id=connector, connections = connectee))
        db.session.commit()

    connector_instance.connections += ";" + connectee 
    connectee_instance.connections += ";" + connector 
    db.session.commit()
    connectee_instance.close()
    connector_instance.close()
    return True
    


def free(user_id):
    if db.session.query(Calendars).get(connector) is None:
        return None
    available_members = []
    connector = db.session.query(Connections).get(user_id)
    connections = connector.connections.split(';')
    for connected_id in connections:
        calendar = db.session.query(Calendars).get(connected_id)
        if available(connected_id, calendar):
            available_members.add(client.users_info(user=connected_id)['user']['real_name'])
    free_view = get_block_view('free.json')

    string = ""
    for member in available_members:
        if available_members.index(member) == -1:
            string += ' and ' + member
            break
        string += member + ', '
    
    add_section_string(free_view, string)
    return free_view


def available(user_id, calendar):
    for component in calendar.walk():
        if 'DTSTART' in component.keys() and 'DTEND' in component.keys():
            if within_time(component.decoded('DTSTART').datetime(), component.decoded('DTEND').datetime(), datetime.datetime.now()):
                return False

    return True

def display(user_id, date):
    calendar = db.session.query(Calendars).get(user_id)

    if calendar is None:
        return None

    timetable = get_block_view("display_timetable")
    
    for i in range(0, 7):
        date = date_from_requested_date(i, date)
        day_string = "_ " + days[i] + " " + date.day + " " + calendar.month_name[date.month]
        add_section_string(timetable, day_string)

        day_schedule = construct_day_schedule(i, date, calendar)
        for day in day_schedule:
            add_section_string(timetable, day)

    return timetable



def construct_day_schedule(date, calendar):
    day_schedule = []
    for component in calendar.walk():
        if component.name == 'VEVENT' and component.decoded('DTSTART').time() != component.decoded('DTEND').time():
            name = component.get('summary')
            starttime = component.decoded('DTSTART').datetime()
            endtime = component.decoded('DTEND').datetime()
            location = component.get('location')
            if date.equals(datetime.date.today()):
                if within_time(date, endtime, datetime.datetime.now().datetime()):
                    string = "*" + name + ": " + starttime + " - " + endtime + "* | *" + location + "*"
                    day_schedule.append(string)
                    continue

            if recurring_component_happens_on_date(component, date):
                for generated_date in generate_dates(component.get('RRULE')):
                    if generated_date.equals(date):
                        if date.equals(datetime.date.today()) and within_time(date, endtime, datetime.datetime.now().datetime()):
                            string = "*" + name + ": " + str(generated_date.time()) + " - " + str(generated_date.time() + endtime.time() - starttime.time()) + "* | *" + location + "*"    
                        else:
                            string = name + ": " + str(generated_date.time()) + " - " + str(generated_date.time() + endtime.time() - starttime.time()) + " | " + location 
                    
            else:
                if component.starttime.date().equals(date):
                    if date.equals(datetime.date.today()) and within_time(date, endtime, datetime.datetime.now().datetime()):
                        string = "*" + name + ": " + starttime + " - " + endtime + "* | *" + location + "*"
                        day_schedule.append(string)
                    else:
                        string = name + ": " + starttime + " - " + endtime + " | " + location 
                        day_schedule.append(string)


    day_schedule.sort(key=sortKey)
    return day_schedule


def sortKey(event):
  split_string = event.split(separator=": ")
  split_string = split_string[1]
  split_string = split_string.split(" - ")
  starttime = split_string[0]
  return starttime
            
def add_section_string(view, text):
    section_string['text'] = text
    timetable['blocks'].insert(0, section_string)


def date_from_requested_date(weekday, date):
    if weekday < date.weekday():
        return date - datetime.timedelta(days=(date.weekday() - weekday))
    else:
        return date - datetime.timedelta(days=(weekday - date.weekday()))

def recurring_component_happens_on_date(event, date):
    if rrule['UNTIL'][0].date() < date:
        if date in generate_dates(rrule):
            return True

    return True

def within_time(starttime, endtime, time):
    return (starttime.date() <= time.date()) and (time.date() <= endtime.date()) and (starttime.time() <= time.time()) and (time.time() <= endtime.time())


def generate_dates(rrule):
    freq = rrule['FREQ'][0]
    dtstart = None
    interval=1
    wkst=None
    count=None
    until=None
    bysetpos=None
    bymonth=None
    bymonthday=None
    byyearday=None
    byeaster=None
    byweekno=None
    byweekday=None
    byhour=None
    byminute=None
    bysecond=None
    if 'DTSTART' in rrule.keys():
        dtstart = rrule['DTSTART'][0]
    if 'INTERVAL' in rrule.keys():
        interval = int(rrule['INTERVAL'][0])
    if 'WKST' in rrule.keys():
        wkst = weekdays[rrule['WKST'][0]]
    if 'COUNT' in rrule.keys():
        count = int(rrule['COUNT'][0])
    if 'UNTIL' in rrule.keys():
        until = rrule['UNTIL'][0]
    if 'BYSETPOS' in rrule.keys():
        bysetpos = [int(numeric_string) for numeric_string in rrule['BYSETPOS']]
    if 'BYMONTH' in rrule.keys():i
        bymonth = [int(numeric_string) for numeric_string in rrule['BYMONTH']]
    if 'BYMONTHDAY' in rrule.keys():
        bymonthday = [int(numeric_string) for numeric_string in rrule['BYMONTHDAY']]
    if 'BYYEARDAY' in rrule.keys():
        byyearday = [int(numeric_string) for numeric_string in rrule['BYYEARDAY']]
    if 'BYEASTER' in rrule.keys():
        byeaster = [int(numeric_string) for numeric_string in rrule['BYEASTER']]
    if 'BYWEEKNO' in rrule.keys():
        byweekno = [int(numeric_string) for numeric_string in rrule['BYWEEKNO']]
    if 'BYWEEKDAY' in rrule.keys():
        byweekday = [int(numeric_string) for numeric_string in rrule['BYWEEKDAY']]
    if 'BYHOUR' in rrule.keys():
        byhour = [int(numeric_string) for numeric_string in rrule['BYHOUR']]
    if 'BYMINUTE' in rrule.keys():
        byminute = [int(numeric_string) for numeric_string in rrule['BYMINUTE']]
    if 'BYSECOND' in rrule.keys():
        bysecond = [int(numeric_string) for numeric_string in rrule['BYSECOND']]

    return list(rrule(freq=freq, dtstart=dtstart, interval=interval, wkst=wkst, count=count, until=until, bysetpos=bysetpos, bymonth=bymonth, bymonthday=bymonthday, byyearday=byyearday, byeaster=byeaster, byweekno=byweekno, byweekday=byweekday, byhour=byhour, byminute=byminute, bysecond=bysecond))
    
    
    
    

        