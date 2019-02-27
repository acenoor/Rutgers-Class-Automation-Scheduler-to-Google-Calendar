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
from bs4 import BeautifulSoup
from course import Course
from selenium import webdriver
import time
import datetime
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools


def execute():
    username = "aun4"
    password = "OTISA40481n!"

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

    time.sleep(4)

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

    # Split the timings into two for a class if they exist for all courses
    splitTimings(courses)

    # Organize each course object with having a single date and time along with location
    organizeDates(courses)

    printInfo(courses)

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
        print("\tInfo: ")
        print(course_obj.total_description)



if __name__ == "__main__":
    execute()




