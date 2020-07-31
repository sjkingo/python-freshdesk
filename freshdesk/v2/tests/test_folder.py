import datetime

import pytest

from freshdesk.v2.models import Folder


@pytest.fixture
def folder(api):
    return api.folders.get_folder(1)

def test_folder(folder):
    assert isinstance(folder, Folder)
    assert folder.name == 'Folder 1'
    assert folder.description == 'Description'


def test_folder_datetime(folder):
    assert isinstance(folder.created_at, datetime.datetime)
    assert isinstance(folder.updated_at, datetime.datetime)


def test_folder_str(folder):
    assert str(folder) == 'Folder 1'


def test_folder_repr(folder):
    assert repr(folder) == '<Folder \'Folder 1\'>'

def test_create_folder(api):
    folder_data = {
        'name': 'Folder 1',
        'description': 'Description'
    }
    folder = api.folders.create_folder(1, name="Folder 1", description="Description")
    assert isinstance(folder, Folder)
    assert folder.description == folder.description
    assert folder.name == folder.name

def test_update_folder(api):
    folder_data = {
        'name': 'Folder',
        'description': 'Description'
    }
    folder = api.folders.update_folder(1,name="Folder UPDATED", description="Description")
    assert isinstance(folder, Folder)
    assert folder.description == folder.description
    assert folder.name == folder.name

def test_delete_folder(api):
    folder = api.folders.delete_folder(1)
    assert type(folder) == type(None)