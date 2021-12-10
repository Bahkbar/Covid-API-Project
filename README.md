# Coronavirus Dashboard
## Introduction
This project acts as an information hub for news and data relating to Coronavirus within the UK. 

Up to date Coronavirus statistics are received via the [UK Government's COVID-19 API Service](https://coronavirus.data.gov.uk/details/developers-guide).

Relevant news articles pertaining to Coronavirus are received using [News API](https://newsapi.org).

All this information is displayed on a localhost page (hosted on [127.0.0.1:5000/](127.0.0.1:5000/)). Using this dashboard, users can not only view Coronavirus data and news articles, but schedule updates to these datum.

Development of this project was for the capstone project of ECM1400 Programming at the University of Exeter

## Prerequisites

Developed using Python 3.9.6

Listed below are the required dependencies that require installation for the Coronavirus Dashboard to function as intended.

Note: If pip does not work, try using pip3 instead.

UK COVID-19 API:
```bash
$ pip install uk-covid19
```
Flask:
```bash
$ pip install Flask
```

## Usage

Before you can use this project, you will need to acquire your own news API key to fetch and access relevant Coronavirus news articles. This can be attained from [https://newsapi.org/register](https://newsapi.org/register).

Note: An API key is not required for accessing Coronavirus data using the UK.

Once you have your own API key, go to the config.json file located within the package and paste your API key next to the key 'news_api', making sure the key is enclosed by quotation marks.

```python
{
    "news_api": "INSERT API KEY HERE",
    ...
}
```

### Customising Configuration File
The associated configuration file - config.json - contains several parameters that can be modified to customise and tailor the dashboard to your needs.

#### News_api
As aforementioned, this holds the news.org API key used to access relevant Covid news articles

#### local_location
local_location refers to a LTLA (Lower Tier Local Authority) that you would like to see Coronavirus data about. The default value for this is "Exeter".

A list of valid LTLA's can be found [here](https://geoportal.statistics.gov.uk/datasets/967a3660c4aa49819731ceefe4008d76/explore)

#### national_location
national_location refers to a nation that you would like to see Coronavirus data about. The default value for this is "England"

The valid nation values are:

England, Northern Ireland, Scotland, and Wales

#### news_API_domains
news_API_domains contains any domains that you would like to see news articles from. Only news sites whose domains are listed will have their articles fetched.
If altering, make sure each domain is comma separated like the examples below.

#### covid_terms
covid_terms contains the keywords that are used to filter which news articles are fetched. If the article contains one of these keywords, it will be fetched and shown on the dashboard.
Ensure each keyword is separated/formatted as shown below.

#### num_articles_at_once
num_articles_at_once refers to how many news articles will be visible at once. The default value - 5 - means that at any one time, only five news articles will be shown, to see more you will have to delete an article to "clear up space". 

If changing, ensure the value does not exceed the value of "page_size".

#### page_size
page_size relates to how many news articles are fetched using the news.org API at any one time. This can take any positive value up to and including 100.

```python
{
    "news_api": "INSERT API KEY HERE", 
    "local_location": "Exeter",
    "national_location": "England",
    "news_API_domains": "bbc.co.uk, channel4.co.uk, itv.co.uk, skynews.com, independent.co.uk",
    "covid_terms":  "Covid Coronavirus Covid-19",
    "num_articles_at_once": 5,
    "page_size": 50
}
```
### Using the dashboard

To start the application, enter your command line/terminal and navigate to project folder directory.
Then run the application by entering: 

"python3 user_interface.py"
 
Upon running the application and heading to [127.0.0.1:5000/](127.0.0.1:5000/) you will be presented with four main sections:

#### News Articles
On the right of the screen, you will see news articles relating to Coronavirus. Each article has its own individual widget with different features.

The top section displays the article's source and title, while the main body contains a brief description of the article.

There is a cross in the top right that will allow you to "delete" a news article, meaning it will never appear again, unless you choose to remove it from the "deleted_articles.txt" file.

There is also a "Read Article" hyperlink that will open in a new tab and allow you to read the full article.

#### Coronavirus Data
In the middle are four metrics:
- local covid cases in the last seven days
- national covid cases in the last seven days
- current hospital cases from covid
- total national covid deaths

#### Setting Updates
The middle section of the dashboard allows the user to set updates for the news articles, covid data, or both. This will refresh the articles/data and replace them with the most up to date information possible.

When setting an update first select a time you want this update to take place at.

Then enter a name for the update (note this step is required to submit an update)

Next you have a combination of checkboxes to choose from:
- You can create an update for just news articles, just covid data or both news articles and data.
- Furthermore, if you tick repeat update, this update will repeat every 24 hours.
Once you are happy with your chosen update, click submit and the update will be scheduled.

#### Update Toasts
The leftmost section will display all currently scheduled update, including whether it is set to repeat, what datum will be updated and at what time this update will take place. (Note: the dashboard will "refresh" every 60 seconds after launch, so an update might not take place as soon as that minute is reached.

There is also a cross to delete any updates to prevent them from happening.

## Documentation
Below are the docstrings (summaries) of each function from each module, summarising what they do and how they do this.
### user_interface.py
The user_interface module is responsible for handling the rendering and displaying of the user interface.

#### update_interface()
Reads in the latest articles and passes them into the render template, before returning the render template.

        Parameters:
            None
        Returns:
            render_template(): Values to pass into the template.

#### index()
Main function called when the webpage is accessed. Starts schedulers, and checks to see if the user modifies anythings on the site that requires an action to happen.

#### delete_update_toasts(toast_title: str) -> None:
Removes the update toast to be deleted from the list of scheduled update toasts.

        Parameters:
            toast_title (str): Title of the update toast to be deleted.

        Returns:
            None

#### schedule_toast_update(time_till_update: int, update_name: str) -> Event:

Adds a toast update to the scheduler

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            toast_update (event): The news update event that has been scheduled.

#### schedule_news_update(time_till_update: int, update_name: str, is_repeating: bool) -> Event:
Adds a news update to the scheduler

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            update (event): The news update event that has been scheduled.

####schedule_covid_update(time_till_update: int, update_name: str, is_repeating: bool) -> Event:
Calls the covid data handler's event schedule

        Parameters:
            time_till_update (int): Number of seconds until the update should be executed.
            update_name (str): Name of the update to be scheduled.

        Returns:
            update (event): The covid update event that has been scheduled.

#### time_converter(update_time: str) -> int:
Calculates and returns how many seconds are between the current time and the time of the scheduled update

        Parameters:
            update_time (str): Time of the scheduled update in HH:MM format.

        Returns:
            time_difference (int): Number of seconds until the scheduled update is completed.

        Raises:
            ValueError: If no value is inputted for update_time.

### covid_data_handler
Module to handle all covid data api requests and future updates.

#### parse_csv_data(csv_filename: str) -> list:
Opens a CSV file for reading and converts the contents to a list of lists of strings.

        Parameters:
            csv_filename (str): Name of the CSV file.

        Returns:
            csv_data_list (List[List[str]]): A list of list of strings containing the contents of the CSV file.

#### process_covid_csv_data(covid_csv_data: list) -> Tuple[int, int, int]:
Loops through the covid data list and returns the values for cases in the last seven days, hospital cases, and total_deaths

        Parameters:
            covid_csv_data (List[List[str]]): The covid data from the CSV filters.

        Returns:
            last7days_cases, current_hospital_cases, total_deaths (Tuple[int,int,int]):
                Cases in last 7 days, current hospital cases and total deaths.

#### first_non_null_entry_csv(covid_data: list, column_index: int) -> int:
Iterates through the relevant column in a given data structure and returns the
        index of the first non-null value.

        Parameters:
            covid_data (List[List[str]]): List of covid data from CSV file.
            column_index (int): Index of the column we want the first non-null value from.
        
        Returns:
            i (int): Index of the first non-null value of the required metric.

#### covid_API_request(location: str = "Exeter", location_type: str = "ltla") -> dict:
Covid API request that fetches up to date information for the structures listed in covid_structure.

        Parameters:
            location (str) (Default="Exeter"): The location to fetch covid data about.
            location_type (str) (Default="ltla"): The type of area the location is.
        Returns:
            data (dict): Dictionary of covid data from the specified location

#### first_non_null_entry_api(covid_api_data: dict, value: str) -> int:
Iterates through the given covid_api_data and returns the index of first non-null entry for a certain metric.

        Parameters:
            covid_api_data (dict): Covid data fetched from PHE Covid API.
            value (str): The metric we are interested in i.e. "areaName"

        Returns:
            i (int): index of the first non-null entry for a certain metric

#### schedule_covid_updates(update_interval: int, update_name: str, is_repeating: bool) -> Event:
Schedules a covid data update to occur after a given number of seconds have occurred.

        Parameters:
            update_interval (int): The number of seconds until the update is to executed.
            update_name (str): The name of the update
            is_repeating (bool): Whether or not the update should be repeated

        Returns:
            update (Event): The scheduled covid update event

#### update_covid_data(update_name: str, is_repeating: bool) -> Tuple[dict, dict]:
Calls the API request function, passing in the location variables and deletes any update toasts related.

        Parameters:
            update_name (str): The name of the update.
            is_repeating (bool): Whether or not the update should be repeated.

        Returns:
            local_data, national_data (Tuple[Dict, Dict]): Covid data for local area and nation.

#### initial_covid_data() -> Tuple[dict, dict]:
Initial covid data to be shown upon starting the program.

        Parameters:
            None

        Returns:
            local_data, national_data (Tuple[dict, dict]): Covid data for local area and nation.

### covid_news_handling
Module to handle all covid news article request and future updating.

#### news_API_request(covid_terms: str = f"{covid_keywords}") -> list:
API request that fetches all news articles that have terms matching 'covid_terms' then creates a list with the wanted fields from each of the news articles. This list is then checked against a file containing deleted articles and any matches are deleted from the list. The first n articles are then returned.

        Parameters:
            covid_terms (str): The terms used to filter the fetched news articles.

        Returns:
            capped_news_articles (list): A list of the first n news articles.

#### def first_n_news_articles(local_articles: list([dict]), local_num_articles_at_once: int, local_page_size: int) -> list[dict]:
Function to create a sublist of news articles, returning n articles where n is how many articles are to be displayed at any one time.

        Parameters:
            local_articles (list[dict]): List of news articles to be truncated.
            local_num_articles_at_once (int): Number of articles to be included in the sublist.
            local_page_size (int): The total number of articles retrieved, acts as the upper limit for local_num_articles_at_once.

        Returns:
            capped_news_articles (list[dict]): The truncated sublist of news articles.

#### def remove_deleted_articles(news_articles: list[dict]) -> list[dict]:
Reads a file containing a list of deleted news articles and removes any deleted articles from the news articles list.

        Parameters:
            news_articles (list[dict]): List of news articles before removal of deleted articles.
        Returns:
            news_articles (list[dict]): List of news articles after removal of deleted articles.

#### def delete_news_article(articles: list[dict], title: str) -> list[dict]:
Iterates through the news articles and deletes any articles that match the title of the news article to be deleted.

        Parameters:
            articles (list[dict]): The list of current news articles.
            title (str): The title of the news article that is to be deleted.
        Returns:
            articles (list[dict]): The updated list of news articles excluding the deleted article.

#### def update_news(update_name: str, is_repeating: bool) -> list[dict]:
Calls the news_API_request function to return up-to-date news articles.

        Parameters:
            update_name(str): Name of the news update.
            is_repeating(bool): Whether or not update is to be repeated.
        Returns:
            articles (list[dict]): Updated list of news articles.


### sys.log
sys.log is a logging file where all actions, exceptions and errors are raised to.
For example, a log entry is created whenever an update is scheduled, news articles fetched, the application is started etc.

## Testing
Testing can be used by running any module beginning with "test_". These modules have a series of tests that ensure the program is functioning as intended.
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.


## License
[MIT](https://choosealicense.com/licenses/mit/)