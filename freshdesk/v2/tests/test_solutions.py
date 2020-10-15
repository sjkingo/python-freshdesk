# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import sys
from mock import patch, ANY

import pytest

from freshdesk.v2.models import (
    SolutionCategory,
    SolutionFolder,
    SolutionArticle,
)

TEST_CATEGORY = 2
TEST_FOLDER = 3
TEST_ARTICLE = 4

@pytest.fixture
def solution_category(api):
    return api.solutions.categories.get_category(TEST_CATEGORY)


def test_solution_category_str(solution_category):
    assert str(solution_category) == "General Category"


def test_solution_category_repr(solution_category):
    assert repr(solution_category) == "<SolutionCategory 'General Category' #%d>" % TEST_CATEGORY


def test_get_solution_category(solution_category):
    assert isinstance(solution_category, SolutionCategory)
    assert solution_category.id == TEST_CATEGORY 
    assert solution_category.name == 'General Category'
    assert isinstance(solution_category.created_at, datetime.datetime)
    assert isinstance(solution_category.updated_at, datetime.datetime)


def test_encoding():
    assert sys.getdefaultencoding() == 'utf-8'

def test_get_solution_category_translated(api, solution_category):
    category_fr = api.solutions.categories.get_category_translated(TEST_CATEGORY, 'fr')
    assert isinstance(category_fr, SolutionCategory)
    assert category_fr.id == solution_category.id
    assert category_fr.name == u'Catégorie générale'
    # we want to test whether the translated category was made after the original
    assert isinstance(category_fr.created_at, datetime.datetime)
    assert category_fr.created_at > solution_category.created_at


def test_list_solutions_categories(api, solution_category):
    categories = api.solutions.categories.list_categories()
    assert isinstance(categories, list)
    assert len(categories) == 1
    assert isinstance(categories[0], SolutionCategory)
    assert categories[0].id == TEST_CATEGORY
    assert categories[0].id == solution_category.id

@pytest.fixture
def solution_folder(api):
    return api.solutions.folders.get_folder(TEST_FOLDER)


def test_solution_folder_str(solution_folder):
    assert str(solution_folder) == "Getting Started"


def test_solution_folder_repr(solution_folder):
    assert repr(solution_folder) == "<SolutionFolder 'Getting Started' #%d>" % TEST_FOLDER


def test_get_solution_folder(solution_folder):
    assert isinstance(solution_folder, SolutionFolder)
    assert solution_folder.id == TEST_FOLDER
    assert solution_folder.name == "Getting Started"
    assert isinstance(solution_folder.created_at, datetime.datetime)
    assert isinstance(solution_folder.updated_at, datetime.datetime)


def test_get_solution_folder_translated(api, solution_folder):
    folder_fr = api.solutions.folders.get_folder_translated(TEST_FOLDER, 'fr')
    assert isinstance(folder_fr, SolutionFolder)
    assert folder_fr.id == solution_folder.id
    assert folder_fr.name == 'Commencer'
    # we want to test whether the translated folder was made after the original
    assert isinstance(folder_fr.created_at, datetime.datetime)
    assert folder_fr.created_at > solution_folder.created_at


def test_list_solution_folders(api, solution_folder):
    folders = api.solutions.folders.list_from_category(TEST_CATEGORY)
    assert isinstance(folders, list)
    assert len(folders) == 1
    assert isinstance(folders[0], SolutionFolder)
    assert folders[0].id == TEST_FOLDER
    assert folders[0].id == solution_folder.id


def test_list_solution_folders_translated(api, solution_folder):
    folders = api.solutions.folders.list_from_category_translated(TEST_CATEGORY, 'fr')
    assert isinstance(folders, list)
    assert len(folders) == 1
    assert isinstance(folders[0], SolutionFolder)
    assert folders[0].id == TEST_FOLDER
    assert folders[0].name == 'Commencer'

@pytest.fixture
def solution_article(api):
     return api.solutions.articles.get_article(TEST_ARTICLE)


def test_solution_article_str(solution_article):
    assert str(solution_article) == "Changing account details"


def test_solution_folder_repr(solution_article):
    assert repr(solution_article) == "<SolutionArticle 'Changing account details' #%d>" % TEST_ARTICLE


def test_get_solution_article(solution_article):
    assert isinstance(solution_article, SolutionArticle)
    assert solution_article.id == TEST_ARTICLE
    assert solution_article.title == "Changing account details"
    assert solution_article.status == 'published'
    assert solution_article.agent_id == 432
    assert solution_article.folder_id == TEST_FOLDER
    assert solution_article.category_id == TEST_CATEGORY
    assert isinstance(solution_article.created_at, datetime.datetime)
    assert isinstance(solution_article.updated_at, datetime.datetime)
    assert "foo" in solution_article.tags
    assert "bar" in solution_article.tags
    assert solution_article.seo_data['meta_title'] == 'seo_account'
    assert solution_article.seo_data['meta_description'] == 'seo_account_description'


def test_get_solution_article_translated(api, solution_article):
    article_fr = api.solutions.articles.get_article_translated(TEST_ARTICLE, 'fr')
    assert isinstance(article_fr, SolutionArticle)
    assert article_fr.id == solution_article.id
    assert article_fr.title == u'Modifier les détails du compte'
    # we want to test whether the translated solution article was made after the original
    assert isinstance(article_fr.created_at, datetime.datetime)
    assert article_fr.created_at > solution_article.created_at


def test_list_solution_articles(api, solution_article):
    articles = api.solutions.articles.list_from_folder(TEST_FOLDER)
    assert isinstance(articles, list)
    assert len(articles) == 2
    assert isinstance(articles[0], SolutionArticle)
    assert articles[0].id == TEST_ARTICLE
    assert articles[0].id == solution_article.id


def test_list_solution_articles_translated(api, solution_article):
    articles_fr = api.solutions.articles.list_from_folder_translated(TEST_FOLDER, 'fr')
    assert isinstance(articles_fr, list)
    assert len(articles_fr) == 2
    assert isinstance(articles_fr[0], SolutionArticle)
    assert articles_fr[0].id == TEST_ARTICLE
    assert articles_fr[0].id == solution_article.id
    assert articles_fr[0].title == 'Modifier les détails du compte'