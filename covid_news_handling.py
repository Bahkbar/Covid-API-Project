"""
Module to handle all covid news article request and future updating.
"""
import json
import logging
from datetime import date, timedelta
import requests
from flask import Markup
import user_interface as ui

with open("config.json", "r", encoding="utf-8") as config:
    # Opens config file and reads in and assigns each variable
    json_file = json.load(config)
api_key = json_file["news_api"]
local_location = json_file["local_location"]
national_location = json_file["national_location"]
included_domains = json_file["news_API_domains"]
covid_keywords = json_file["covid_terms"]
num_articles_at_once = json_file["num_articles_at_once"]
page_size = json_file["page_size"]


def news_API_request(covid_terms: str = f"{covid_keywords}") -> list:
    """
    API request that fetches all news articles that have terms matching 'covid_terms'
    then creates a list with the wanted fields from each of the news articles.
    This list is then checked against a file containing deleted articles and any
    matches are deleted from the list.
    The first n articles are then returned.

        Parameters:
            covid_terms (str): The terms used to filter the fetched news articles.

        Returns:
            capped_news_articles (list): A list of the first n news articles.
    """
    keywords = covid_terms  # .replace(", "," OR ")
    base_url = "https://newsapi.org/v2/everything?"
    # Calculate the date seven days ago.
    date_7_days_ago = (date.today() - timedelta(7)).isoformat()
    complete_url = (
        f"{base_url}q=({keywords})&sortBy&from={date_7_days_ago}&pageSize={page_size}&domains={included_domains}&apiKey={api_key}")
    news = requests.get(complete_url).json()  # API request
    logging.info("News articles fetched")
    news_articles = []  # Empty list to add news articles to
    # Loops through each article and creates a new dictionary with only relelvant article parts.
    for i in news['articles']:
        news_articles.append(
            {
                "title": f"{i['author']} - {i['title']}",
                "content": f"{i['description']} <br><a href='{i['url']}' target='_blank'>Read Article</a>",
                "description": i['content'],
                "url": i['url'],
            })
    for i in news_articles:
        # Allows HTML to be treated and executed as HTML, not text.
        i["content"] = Markup(i['content'])
    # Removes articles that have been deleted from article list
    news_articles = remove_deleted_articles(news_articles)
    with open("news_articles.json", 'w', encoding='utf-8') as arts:
        json.dump(news_articles, arts)  # Writes articles to a json file
    capped_news_articles = first_n_news_articles(
        news_articles, num_articles_at_once, page_size)  # Returns list of first N articles
    return capped_news_articles


def first_n_news_articles(local_articles: list([dict]),
    local_num_articles_at_once: int, local_page_size: int) -> list[dict]:
    """
    Function to create a sublist of news articles, returning n articles where n is how many
        articles are to be displayed at any one time.

        Parameters:
            local_articles (list[dict]): List of news articles to be truncated.
            local_num_articles_at_once (int): Number of articles to be included in the sublist.
            local_page_size (int): The total number of articles retrieved,
                acts as the upper limit for local_num_articles_at_once.

        Returns:
            capped_news_articles (list[dict]): The truncated sublist of news articles.
    """
    capped_news_articles = []  # Creates empty list
    # If the required number of articles is greater than total number of articles
    if local_num_articles_at_once > local_page_size:
        # Set required number of articles to the total number of articles
        local_num_articles_at_once = local_page_size
    try:
        # Creates sublist containing how many articles are wanted
        capped_news_articles = local_articles[:local_num_articles_at_once]
    except IndexError:
        logging.exception("Index Error")
    return capped_news_articles


def remove_deleted_articles(news_articles: list[dict]) -> list[dict]:
    """
    Reads a file containing a list of deleted news articles and removes
    any deleted articles from the news articles list.

        Parameters:
            news_articles (list[dict]): List of news articles before removal of deleted articles.
        Returns:
            news_articles (list[dict]): List of news articles after removal of deleted articles.
    """
    with open('deleted_articles.txt', 'r', encoding='utf-8') as file:
        for line in file:  # For each line in the file
            # For each index and value in each article
            for index, value in enumerate(news_articles):
                # If the title in the file matches the article's title
                if news_articles[index]['title'] in line:
                    # Delete that news article from the article list
                    del news_articles[index]
    logging.info("Deleted articles removed from article list")
    return news_articles


def delete_news_article(articles: list[dict], title: str) -> list[dict]:
    """
    Iterates through the news articles and deletes any articles that match the title
    of the news article to be deleted.

        Parameters:
            articles (list[dict]): The list of current news articles.
            title (str): The title of the news article that is to be deleted.
        Returns:
            articles (list[dict]): The updated list of news articles excluding the deleted article.
    """
    for i in range(len(articles)):  # For the length of the list of articles
        # If the article title matches the deleted article title
        if articles[i]['title'] == title:
            del articles[i]  # Delete said article
            logging.info(f"Deleted news article {title}")
            break
    with open('deleted_articles.txt', 'a', encoding='utf-8') as file:
        file.write(title + "\n")  # Write deleted article to file
    logging.info("Deleted articles written to file")
    return articles


def update_news(update_name: str, is_repeating: bool) -> list[dict]:
    """
    Calls the news_API_request function to return up-to-date news articles.


        Parameters:
            update_name(str): Name of the news update.
            is_repeating(bool): Whether or not update is to be repeated.
        Returns:
            articles (list[dict]): Updated list of news articles.
    """
    try:
        articles = news_API_request()  # Fetches articles from the API.
        # Removes deleted articles from the list of articles.
        articles = remove_deleted_articles(articles)
        logging.info("News articles updated")
        ui.delete_update_toasts(update_name)
        with open("news_articles.json", "w", encoding="utf-8") as arts:
            json.dump(articles, arts)  # Writes articles to json file
        logging.info("News articles successfully written to file")
        # Schedules another update for 24 hours time.
        ui.news_scheduler.enter(86400, 1, update_news,
                                update_name, is_repeating)
    except TypeError:
        logging.exception("Type Error")


if __name__ == "__main__":
    print()
