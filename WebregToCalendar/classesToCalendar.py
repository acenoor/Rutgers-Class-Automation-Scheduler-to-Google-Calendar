#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 17:45:08 2018

@author: anoorzaie

clientid:
    922330167237-3sjhb2gf3rbah9erblofp7ada12d0lq2.apps.googleusercontent.com
    
clientsecret:
--3hgGhZ5WngV-9q90sGfOdP
"""

from __future__ import print_function

import os
from pytz import timezone
import pytz
from bs4 import BeautifulSoup
from course import Course
from EventJSON import event
from selenium import webdriver
import time
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


FREQUENCY_PART_1 = 'RRULE:FREQ=WEEKLY;UNTIL='
FREQUENCY_PART_2 = 'YYYYMMDD' # <- depending on semester
SEMESTER_END_DATE = {'Fall': ['12', '15'], 'Spring': ['05','10'], 'Summer':['08','18']}

def execute():
    username = "aun4"
    password = "tawakul786!"

    chromedriver = "/Users/anoorzaie/Downloads/chromedriver"

    driver = webdriver.Chrome(chromedriver)
    driver.get('https://sims.rutgers.edu/webreg/chooseSemester.htm')

    user = driver.find_element_by_xpath('//*[@id="username"]')
    user.send_keys(username)

    passw = driver.find_element_by_xpath('//*[@id="password"]')
    passw.send_keys(password)

    driver.find_element_by_xpath('//*[@id="fm1"]/fieldset/div[6]/input[4]').click()

    driver.find_element_by_xpath('//*[@id="submit"]').click()

    source = driver.page_source
    soup = BeautifulSoup(source, 'lxml')

    id1 = '//*[@id="sidebar"]/dl['
    id2 = ']/dd/dl/dd['
    id3 = ']'

    course_name_part_1 = '//*[@id="sidebar"]/dl['
    course_name_part_2 = ']/dt/span/b'

    #//*[@id="sidebar"]/dl[1]/dd/dl/dd/text()[1]

    time.sleep(2)

    info = []
    courses = {}
    course_count = 1
    
    # to split timings seperately do it off of spaces
    while(True):
        if(course_count > 5):
            break
        xpath_course = course_name_part_1 + str(course_count) + course_name_part_2
        course_name = driver.find_element_by_xpath(xpath_course).text
        courses[course_name] = Course(course_name)
        info1 = id1 + str(course_count) + id2 + '1' + id3
        description1 = driver.find_element_by_xpath(info1).text
#        info2 = id1 + str(course_count) + id2 + '2' + id3
#        description2 = driver.find_element_by_xpath(info2).text
        if (description1 == "By-arrangement course"):
            if course_name in courses:
                del courses[course_name]
            course_count += 1
            continue
        elif courses[course_name].description_1 == []:
            
            courses[course_name].description_1.append(description1)
        else:
            courses[course_name].description_2.append(description1)
        course_count += 1
    
    # Check whether it is the fall semester or spring Semester and populate the recurrence field of Google Calendar API, depending on the semester
    CheckSemesterAndFillRecurrenceJSON(driver)

    # Split the timings into two for a class if they exist for all courses
    splitTimings(courses)

    # Organize each course object with having a single date and time along with location
    organizeDates(courses)

    # Convert AM/PM time to military time
    organizeTime(courses)

    # Find the start date since the date is dependent upon when the script is ran
    convertTimeToRFC3339(courses)

    #Fill JSON with classes and make service call

    # Making sure everything is correct for each course
    printInfo(courses)   

def convertTimeToRFC3339(courses):
    # https://stackoverflow.com/questions/4770297/convert-utc-datetime-string-to-local-datetime-with-python
    # This will help out with the conversion of UTC time to EST
    eastern_time_zone = timezone('US/Eastern')
    for couse_name, course_obj in courses.items():
        for description in course_obj.total_description:
            day_int = course_obj.dateConversion[description[0]]
            now = datetime.now()
            schedule_day = datetime(now.year, now.month, now.day)
            while(True):
                if schedule_day.weekday() == day_int:
                    break
                    pass
                else:
                    schedule_day = schedule_day + timedelta(days=1)
            start_time_list = description[1].split(":")
            start_time_hour = int(start_time_list[0])
            start_time_minute = int(start_time_list[1])

            end_time_list = description[2].split(":")
            end_time_hour = int(end_time_list[0])
            end_time_minute = int(end_time_list[1])

            description[0] = eastern_time_zone.localize(datetime(schedule_day.year, schedule_day.month, schedule_day.day, start_time_hour, start_time_minute))
            datetime_end_time = eastern_time_zone.localize(datetime(schedule_day.year, schedule_day.month, schedule_day.day, end_time_hour, end_time_minute))
            description.insert(1, datetime_end_time)




def organizeTime(courses):
    # Steps
    # 1. for every course in the dictionary and for every sub-array within the total_description, extract the two dates
    # 2. Convert those two dates into military time and append the start and end time within that subarray
    # i.e end goal is to make the total_description look like: [['Monday', '10:20:00', '11:40:00', 'BRR-5073 Liv']]
    for course_name, course_obj in courses.items():
        for description in course_obj.total_description:
            descr_list = description[1].split(" ")
            start_time = descr_list[0] + ":00" + descr_list[1]
            end_time = descr_list[3] + ":00" + descr_list[4]
            start = datetime.strptime(start_time, '%I:%M:%S%p').strftime('%H:%M:%S')
            end = datetime.strptime(end_time, '%I:%M:%S%p').strftime('%H:%M:%S')
            location = descr_list[5] + " " + descr_list[6]
            description[1:] = [start, end, location]
            


def organizeDates(courses):

    for course_name, course_obj in courses.items():
        class_timings_list = course_obj.get_description()
        for class_timing in class_timings_list:
            # first space index
            first_space_index = class_timing.index(" ")
            date = class_timing[:first_space_index]
            # find the days it corresponds to which returns a list of strings corresponding to the date
            dates_list = course_obj.classMap[date]
            time_and_location = class_timing[first_space_index+1:]
            for day in dates_list:
                course_obj.total_description.append([day, time_and_location])





def splitTimings(courses):

    for course_name, course_obj in courses.items():
        # More than two timings in different location so split
        old_description = course_obj.description_1
        descr_list = old_description[0].split("\n")
        if len(descr_list) == 2:
            course_obj.description_1 = [descr_list[0]]
            course_obj.description_2 = [descr_list[1]]
        else:
            course_obj.description_1 = [descr_list[0]]

        
        # if(len(descr_list)==2):
        #     course_obj.description_1 = descr_list[0]
        #     course_obj.description_2 = descr_list[1]
        
        # if old_description.count(" ") > 7:
        #     print("got here")
        #     descr_list = old_description.split(" ")
        #     # split at this point
        #     if "Busch" in descr_list and (descr_list.index("Busch") != len(descr_list)):
        #         print("in busch")
        #         index = old_description.find("Busch") + 5
        #         descrption1 = old_description[:index]
        #         description2 = old_description[index:]
        #         course_obj.description_1 = descrption1
        #         course_obj.description_2 = description2
        #     elif "Liv" in descr_list and (descr_list.index("Liv") != len(descr_list)):
        #         print("in Liv")
        #         index = old_description.find("Liv") + 3
        #         descrption1 = old_description[:index]
        #         description2 = old_description[index:]
        #         course_obj.description_1 = descrption1
        #         course_obj.description_2 = description2
            
            #Do one more for Cook Douglas


            
def printInfo(courses):
    for name, course_obj in courses.items():
        print("Course: " + name)
        for description in course_obj.total_description:
            print(description)
        print()

def CheckSemesterAndFillRecurrenceJSON(driver):
    semester_id = '//*[@id="meta"]/h2'
    semester_text = driver.find_element_by_xpath(semester_id).text.lower()
    current_year = str(datetime.now().year)
    if('spring' in semester_text):
        end_date_month = SEMESTER_END_DATE['Spring'][0]
        end_date_day =  SEMESTER_END_DATE['Spring'][1]
        FREQUENCY_PART_2 = current_year + end_date_month + end_date_day
        print(FREQUENCY_PART_2)
    if('fall' in semester_text):
        print('fall')
    if('summer' in semester_text):
        print('summer')
    print('-------------------')



if __name__ == "__main__":
    execute()




