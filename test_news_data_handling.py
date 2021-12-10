from covid_news_handling import news_API_request
from covid_news_handling import update_news
from covid_news_handling import first_n_news_articles
from covid_news_handling import delete_news_article

def test_news_API_request():
    assert news_API_request()
    assert news_API_request('Covid COVID-19 coronavirus') == news_API_request()

def test_update_news():
    update_news('test', False)

def test_first_n_news_articles():
    articles=[]
    articles.append(
        {
        "title": "1",
        "content": "1",
    }
    )
    articles.append(
        {
        "title": "2",
        "content": "2",
    }
    )
    articles.append(
        {
        "title": "3",
        "content": "3",
    }
    )
    articles.append(
        {
        "title": "4",
        "content": "4",
    }
    )
    assert len(first_n_news_articles(articles, 2, 4)) == 2 

def test_delete_news_article():
    title="1"
    articles=[]
    articles.append(
        {
        "title": "1",
        "content": "1",
    }
    )
    articles.append(
        {
        "title": "2",
        "content": "2",
    }
    )
    articles.append(
        {
        "title": "3",
        "content": "3",
    }
    )
    articles.append(
        {
        "title": "4",
        "content": "4",
    }
    )
    assert len(delete_news_article(articles, title))==3
    
test_update_news()
test_news_API_request()
test_first_n_news_articles()
test_delete_news_article()
