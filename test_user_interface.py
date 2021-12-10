from user_interface import schedule_toast_update
from user_interface import schedule_news_update
from user_interface import schedule_covid_update
from user_interface import time_converter
from time import gmtime
from flask import Flask

def test_schedule_toast_update():
    schedule_toast_update(5,"testUpdate")

def test_schedule_news_update():
    schedule_news_update(5,"testNewsUpdate",False)

def test_schedule_covid_update():
    schedule_covid_update(5,"testCovidUpdate",False)

def test_time_converter():
    test_time="11:30"
    #Convert 11:30 to seconds
    test_time_in_seconds=(11*60*60)+(30*60)
    current_time_in_seconds=(60*60*gmtime().tm_hour)+(60*gmtime().tm_min)+(gmtime().tm_sec)
    assert time_converter(test_time) == abs(test_time_in_seconds-current_time_in_seconds)

test_schedule_toast_update()
test_schedule_covid_update()
test_time_converter()
