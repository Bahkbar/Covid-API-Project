"""
Module to handle all covid data api requests and future updates.
"""
from threading import Event
import logging
import csv
import time
import sched
import json
from typing import Tuple
from uk_covid19 import Cov19API
import user_interface as ui
s = sched.scheduler(time.time, time.sleep)

with open("config.json","r", encoding="utf-8") as config:
    json_file=json.load(config) # Opens config file and reads in and assigns each variable
api_key=json_file["news_api"]
local_location=json_file["local_location"]
national_location=json_file["national_location"]
included_domains=json_file["news_API_domains"]
covid_keywords=json_file["covid_terms"]
num_articles_at_once=json_file["num_articles_at_once"]
page_size=json_file["page_size"]

def parse_csv_data(csv_filename: str) -> list:
    """
    Opens a CSV file for reading and converts the contents to a list of lists of strings.

        Parameters:
            csv_filename (str): Name of the CSV file.

        Returns:
            csv_data_list (List[List[str]]): A list of list of strings containing
                the contents of the CSV file.
    """
    with open(csv_filename, newline=None, encoding='utf-8') as csv_file:
        reader = csv.reader(csv_file)
        csv_data_list = list(reader)
        return csv_data_list


def process_covid_csv_data(covid_csv_data: list) -> Tuple[int, int, int]:
    """
    Loops through the covid data list and returns the values for cases in the last seven days,
        current hospital cases, and total_deaths

        Parameters:
            covid_csv_data (List[List[str]]): The covid data from the CSV filters.

        Returns:
            last7days_cases, current_hospital_cases, total_deaths (Tuple[int,int,int]):
                Cases in last 7 days, current hospital cases and total deaths.
    """
    last7days_cases = 0

    first_hospital_index = first_non_null_entry_csv(covid_csv_data, 5)
    current_hospital_cases = int(covid_csv_data[first_hospital_index][5])

    first_deaths_index = first_non_null_entry_csv(covid_csv_data, 4)
    total_deaths = int(covid_csv_data[first_deaths_index][4])

    first_case_index = first_non_null_entry_csv(covid_csv_data, 6)
    for i in range(first_case_index+1, first_case_index+8):
        last7days_cases += int(covid_csv_data[i][6])

    return last7days_cases, current_hospital_cases, total_deaths


def first_non_null_entry_csv(covid_data: list, column_index: int) -> int:
    """
    Iterates through the relevant column in a given data structure and returns the
        index of the first non-null value.

        Parameters:
            covid_data (List[List[str]]): List of covid data from CSV file.
            column_index (int): Index of the column we want the first non-null value from.
        Returns:
            i (int): Index of the first non-null value of the required metric.
    """
    for i in range(1, len(covid_data)-1):
        if covid_data[i][column_index] != "":  # If value of that index is not null
            return i


def covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> dict:
    """
    Covid API request that fetches up to date information for the structures listed
        in covid_structure.

        Parameters:
            location (str) (Default="Exeter"): The location to fetch covid data about.
            location_type (str) (Default="ltla"): The type of area the location is.
        Returns:
            data (dict): Dictionary of covid data from the specified location
    """
    location_filters = [
        f"areaType={location_type}",
        f"areaName={location}"
    ]
    covid_structure = {
        "date": "date",
        "areaName": "areaName",
        "areaCode": "areaCode",
        "Local 7-Day Infection Rate": "newCasesByPublishDateRollingSum",
        "National 7-Day Infection Rate": "newCasesByPublishDateRollingSum",
        "Hospital Cases": "hospitalCases",
        "Total Deaths": "cumDeaths28DaysByDeathDate"
    }
    api = Cov19API(
        filters=location_filters,
        structure=covid_structure,
    )
    data = api.get_json()
    return data


def first_non_null_entry_api(covid_api_data: dict, value: str) -> int:
    """
    Iterates through the given covid_api_data and returns the index
        of first non-null entry for a certain metric.

        Parameters:
            covid_api_data (dict): Covid data fetched from PHE Covid API.
            value (str): The metric we are interested in i.e. "areaName"

        Returns:
            i (int): index of the first non-null entry for a certain metric
    """
    for i in range(len(covid_api_data["data"])):
        # If value of that key is not empty
        if covid_api_data["data"][i][value] is not None:
            return i


def schedule_covid_updates(update_interval: int, update_name: str, is_repeating: bool) -> Event:
    """
    Schedules a covid data update to occur after a given number of seconds have occurred.

        Parameters:
            update_interval (int): The number of seconds until the update is to executed.
            update_name (str): The name of the update
            is_repeating (bool): Whether or not the update should be repeated

        Returns:
            update (Event): The scheduled covid update event
    """
    update = ui.covid_scheduler.enter(update_interval, 1, update_covid_data, [
                                      update_name, is_repeating])
    return update


def update_covid_data(update_name: str, is_repeating: bool) -> Tuple[dict, dict]:
    """
    Calls the API request function, passing in the location variables
        and deletes any update toasts related.

        Parameters:
            update_name (str): The name of the update.
            is_repeating (bool): Whether or not the update should be repeated.

        Returns:
            local_data, national_data (Tuple[Dict, Dict]): Covid data for local area and nation.
    """
    local_data = covid_API_request(location=f"{local_location}")
    national_data = covid_API_request(f"{national_location}", "Nation")
    # Deletes toasts of update that called update_covid_data
    ui.delete_update_toasts(update_name)
    if is_repeating:
        ui.schedule_covid_update(86400, update_name, is_repeating)
    logging.info("Updating Covid Data")
    return local_data, national_data


def initial_covid_data() -> Tuple[dict, dict]:
    """
    Initial covid data to be shown upon starting the program.

        Parameters:
            None

        Returns:
            local_data, national_data (Tuple[dict, dict]): Covid data for local area and nation.
    """
    local_data = covid_API_request(location=f"{local_location}")
    national_data = covid_API_request(f"{national_location}", "Nation")
    return local_data, national_data


local_covid_data, national_covid_data = initial_covid_data()
csv_data = parse_csv_data('nation_2021-10-28.csv')


# Acquires the indexes of the first non-null value of each required metric.
local_location_index = first_non_null_entry_api(local_covid_data, "areaName")
national_location_index = first_non_null_entry_api(
    national_covid_data, "areaName")
local_7day_infection_rate_index = first_non_null_entry_api(
    local_covid_data, "National 7-Day Infection Rate")
national_7day_infection_rate_index = first_non_null_entry_api(
    national_covid_data, "National 7-Day Infection Rate")
hospital_cases_index = first_non_null_entry_api(
    national_covid_data, "Hospital Cases")
national_total_deaths_index = first_non_null_entry_api(
    national_covid_data, "Total Deaths")

# Acquires the values of the first non-null value of each required metric.
local_location = local_covid_data["data"][local_location_index]["areaName"]
national_location = national_covid_data["data"][national_location_index]["areaName"]
local_7day_infection_rate = local_covid_data["data"][
    local_7day_infection_rate_index]["National 7-Day Infection Rate"]
national_7day_infection_rate = national_covid_data["data"][
    national_7day_infection_rate_index]["National 7-Day Infection Rate"]
hospital_cases = national_covid_data["data"][hospital_cases_index]["Hospital Cases"]
national_total_deaths = national_covid_data["data"][national_total_deaths_index]["Total Deaths"]
