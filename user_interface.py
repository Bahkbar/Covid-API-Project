"""
The user_interface module is responsible for handling the rendering
and displaying of the user interface.
"""

import time
import sched
import json
import logging
from threading import Event
from time import gmtime
from flask import Flask, render_template, request, redirect, Markup
import covid_news_handling as cnh
import covid_data_handler as cdh
logging.basicConfig(filename="sys.log", level=logging.INFO,
                    format='%(asctime)s %(message)s')
logging.info("Application started")

app = Flask(__name__)
covid_scheduler = sched.scheduler(time.time, time.sleep)
news_scheduler = sched.scheduler(time.time, time.sleep)
update_toast_scheduler = sched.scheduler(time.time, time.sleep)

scheduler_updates_toasts = []
# Opens config file and reads in and assigns each variable
with open("config.json", "r", encoding="utf-8") as config:
    json_file = json.load(config)
api_key = json_file["news_api"]
local_location = json_file["local_location"]
national_location = json_file["national_location"]
news_API_domains = json_file["news_API_domains"]
covid_keywords = json_file["covid_terms"]
num_articles_at_once = json_file["num_articles_at_once"]
page_size = json_file["page_size"]

@app.route("/")
def update_interface():
    """
    Reads in the latest articles and passes them into the render template,
    before returning the render template.

        Parameters:
            None
        Returns:
            render_template(): Values to pass into the template.
    """
     # Fetch news articles
    with open("news_articles.json", encoding="utf-8") as arts:
        articles = json.load(arts)  # Loads articles from json file
    first_news_arts = cnh.first_n_news_articles(
        articles, num_articles_at_once, page_size)  # Returns first n news articles
    for i in first_news_arts:
        # Allows HTML to be treated and executed as HTML, not text.
        i["content"] = Markup(i["content"])
    return render_template('index.html',
                           title="Covid Dashboard",
                           favicon="bojo.jpeg",
                           image="covid_logo.jpeg",
                           news_articles=first_news_arts,
                           updates=scheduler_updates_toasts,
                           location=cdh.local_location,
                           local_7day_infections=cdh.local_7day_infection_rate,
                           nation_location=cdh.national_location,
                           national_7day_infections=cdh.national_7day_infection_rate,
                           hospital_cases=(
                               f"Hospital Cases: {cdh.hospital_cases}"),
                           deaths_total=(f"Total Deaths: {cdh.national_total_deaths}"))


@app.route("/index", methods=['GET', 'POST'])
def index():
    """
    Main function called when the webpage is accessed.
    Starts schedulers, and checks to see if the user modifies anythings
    on the site that requires an action to happen.
    """
    covid_scheduler.run(blocking=False)
    news_scheduler.run(blocking=False)
    update_toast_scheduler.run(blocking=False)
    with open("news_articles.json", encoding="utf-8") as arts:
        articles = json.load(arts)
    if request.method == "GET":
        is_repeating = False
        # Title of scheduled update to be created.
        update_title = request.args.get('two')
        # Title of scheduled update to be deleted.
        delete_toast = request.args.get('update_item')
        # Title of the article to be deleted.
        title = request.args.get('notif')
        repeating_str = ""
        if update_title:  # If an update has been submitted via the interface
            # Gets whether or not the scheduled update includes covid data
            covid_update = request.args.get('covid-data')
            # Gets whether or not the scheduled update includes news
            news_update = request.args.get('news')
            # Time at which the update will be executed
            update_time = request.args.get('update')
            # Gets whether or not the scheduled update is to repeat
            repeating_update = request.args.get('repeat')
            if update_time is not None:
                time_till_update = time_converter(update_time)
            if repeating_update:
                repeating_str = "Repeat: "
                is_repeating = True
            if covid_update and news_update:  # If update is for both covid and news
                if time_till_update is None:
                    time_till_update =0
                if time_till_update <= 60:  # If update is in 60 seconds or less
                    cnh.update_news(update_title, is_repeating)
                    cdh.update_covid_data(update_title, is_repeating)
                    if is_repeating:
                        scheduler_updates_toasts.append(
                            {
                                "title": f"{update_title}",
                                "content": f"Repeat Covid and news update scheduled for {update_time}",
                                "updateType": "Both",
                            }
                        )
                else:
                    scheduler_updates_toasts.append(
                        {
                            "title": f"{update_title}",
                            "content": f"Repeat Covid and news update scheduled for {update_time}",
                            "updateType": "Both",
                        }
                    )
                schedule_news_update(
                    time_till_update, update_title, is_repeating)
                schedule_covid_update(
                    time_till_update, update_title, is_repeating)
                schedule_toast_update(time_till_update, update_title)
                update_interface()
            elif news_update:  # If update is for only news
                if time_till_update is None:
                    time_till_update =0
                if time_till_update <= 60:  # If update is in 60 seconds or less
                    cnh.update_news(update_title, is_repeating)
                    if is_repeating:
                        scheduler_updates_toasts.append(
                            {
                                "title": f"{update_title}",
                                "content": f"Repeat Covid update scheduled for {update_time}",
                                "updateType": "News",
                            }
                        )
                else:
                    scheduler_updates_toasts.append(
                        {
                            "title": f"{update_title}",
                            "content": f"{repeating_str}News update scheduled for {update_time}",
                            "updateType": "News",
                        }
                    )
                    schedule_news_update(
                        time_till_update, update_title, is_repeating)
                    schedule_toast_update(time_till_update, update_title)
                update_interface()
            elif covid_update:  # If update is for only covid
                if time_till_update is None:
                    time_till_update =0
                if time_till_update <= 60:  # If update is in 60 seconds or less
                    cdh.update_covid_data(update_title, is_repeating)
                    if is_repeating:
                        scheduler_updates_toasts.append(
                            {
                                "title": f"{update_title}",
                                "content": f"Repeat Covid update scheduled for {update_time}",
                                "updateType": "Covid",
                            }
                        )
                else:
                    scheduler_updates_toasts.append(
                        {
                            "title": f"{update_title}",
                            "content": f"{repeating_str}Covid update scheduled for {update_time}",
                            "updateType": "Covid",
                        }
                    )
                    schedule_covid_update(
                        time_till_update, update_title, is_repeating)
                    schedule_toast_update(time_till_update, update_title)
                update_interface()
            if time_till_update > 60:  # If update is in more than 60 seconds.
                logging.info(
                    f"New scheduled update: {scheduler_updates_toasts[-1]['content']}")
        elif title:
            # Removes article just deleted from article list
            articles = cnh.delete_news_article(articles, title)
            # Removes deleted articles from articles list
            articles = cnh.remove_deleted_articles(articles)
            with open("news_articles.json", 'w', encoding='utf-8') as arts:
                json.dump(articles, arts)  # Writes articles to json file
            update_interface()
        elif delete_toast:
            delete_update_toasts(delete_toast)
    return redirect(request.referrer)  # Redirects to '/' url


def delete_update_toasts(toast_title: str) -> None:
    """
    Removes the update toast to be deleted from the list of scheduled update toasts.

        Parameters:
            toast_title (str): Title of the update toast to be deleted.
            scheduler_updates_toasts (list): List of scheduled update toasts.

        Returns:
            None
    """
    for i in range(len(scheduler_updates_toasts)):  # For length of scheduled update toasts
        if scheduler_updates_toasts[i]['title'] == toast_title:
            del scheduler_updates_toasts[i]
            logging.info(f"Update toast {toast_title} deleted")
            break
        else:
            logging.warning(
                f"Update toast {toast_title} not found in list of updates toasts")


def schedule_toast_update(time_till_update: int, update_name: str) -> Event:
    """
    Adds a toast update to the scheduler

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            toast_update (event): The news update event that has been scheduled.
    """
    toast_update = update_toast_scheduler.enter(
        time_till_update, 1, delete_update_toasts, [update_name, ])
    return toast_update


def schedule_news_update(time_till_update: int, update_name: str, is_repeating: bool) -> Event:
    """
    Adds a news update to the scheduler

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            update (event): The news update event that has been scheduled.
    """
    update = news_scheduler.enter(time_till_update, 1, cnh.update_news, [
                                  update_name, is_repeating])
    update_interface()
    return update


def schedule_covid_update(time_till_update: int, update_name: str, is_repeating: bool) -> Event:
    """
    Calls the covid data handler's event schedule

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            update (event): The covid update event that has been scheduled.
    """
    update = cdh.schedule_covid_updates(
        time_till_update, update_name, is_repeating)
    return update
    # delete_update_toasts(update_name)


def time_converter(update_time: str) -> int:
    """
    Calculates and returns how many seconds are between the current time
        and the time of the scheduled update

        Parameters:
            update_time (str): Time of the scheduled update in HH:MM format.

        Returns:
            time_difference (int): Number of seconds until the scheduled update is completed.

        Raises:
            ValueError: If no value is inputted for update_time.
    """
    try:
        current_hours = gmtime().tm_hour  # Gets the current hour
        current_minutes = gmtime().tm_min  # Gets the current minute
        current_seconds = gmtime().tm_sec  # Gets the current second
        current_time_in_seconds = current_hours*60*60+current_minutes * \
            60+current_seconds  # Gets the current time in seconds

        # Splits HH:MM string into hours and minutes
        update_hours, update_minutes = map(int, update_time.split(':'))
        update_time_in_seconds = update_hours*60*60+update_minutes*60

        # Calculates the difference current time and update time.
        time_difference = update_time_in_seconds-current_time_in_seconds
        if time_difference < 0:
            time_difference = 24*60*60+time_difference
        logging.info(f"Seconds until update: {time_difference}")
        return time_difference  # Returns time until update should execute.
    except ValueError:
        logging.exception("No time inputted")


if __name__ == '__main__':
    articles = cnh.news_API_request()
    app.run()
