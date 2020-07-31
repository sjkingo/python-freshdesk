import pytest
import datetime



from freshdesk.v2.models import Article

@pytest.fixture
def article(api):
    return api.articles.get_article(1)

def test_article(article):
    assert isinstance(article, Article)
    assert article.title == 'Article 1'
    assert article.description == 'Content of the article'

def test_article_datetime(article):
    assert isinstance(article.created_at, datetime.datetime)
    assert isinstance(article.updated_at, datetime.datetime)


def test_article_str(article):
    assert str(article) == 'Article 1'


def test_article_repr(article):
    assert repr(article) == '<Article \'Article 1\'>'


@pytest.fixture
def articles(api):
    return api.articles.list_articles(1)

def test_articles_list(articles):
    assert isinstance(articles, list)
    assert len(articles) == 2
    assert isinstance(articles[0], Article)

def test_create_article(api):
    article_data = {
        'title': 'article',
        'description': 'Description',
        'status': 1
    }
    article = api.articles.create_article(1, **article_data)
    assert isinstance(article, Article)
    assert article.description == 'Content of the article'
    assert article.title == 'Article 1'
    assert article.status == 'draft'

def test_delete_article(api):
    assert api.articles.delete_article(1) is None