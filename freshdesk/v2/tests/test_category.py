import datetime

import pytest

from freshdesk.v2.models import Category


@pytest.fixture
def category(api):
    return api.categories.get_category(1)


def test_list_categories(api, category):
    categories = api.categories.list_categories()
    assert isinstance(categories, list)
    assert len(categories) == 2
    assert categories[0].id == category.id


def test_category(category):
    assert isinstance(category, Category)
    assert category.name == 'Category 1'
    assert category.description == 'Description'


def test_category_datetime(category):
    assert isinstance(category.created_at, datetime.datetime)
    assert isinstance(category.updated_at, datetime.datetime)


def test_category_str(category):
    assert str(category) == 'Category 1'


def test_category_repr(category):
    assert repr(category) == '<Category \'Category 1\'>'

def test_create_category(api):
    category_data = {
        'name': 'Category',
        'description': 'Description'
    }
    category = api.categories.create_category(name="Category 1", description="Description")
    assert isinstance(category, Category)
    assert category.description == category.description
    assert category.name == category.name

def test_update_category(api):
    category_data = {
        'name': 'Category',
        'description': 'Description'
    }
    category = api.categories.update_category(1,name="Category UPDATED", description="Description")
    assert isinstance(category, Category)
    assert category.description == category.description
    assert category.name == category.name

def test_delete_category(api):
    category = api.categories.delete_category(1)
    assert type(category) == type(None)