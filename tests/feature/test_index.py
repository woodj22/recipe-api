import csv
import os

import pytest
from app import create_app

import json

test_file_name = 'test.csv'
dir_path = os.path.dirname(os.path.realpath(__file__))
test_csv_file_path = dir_path + '/' + test_file_name


@pytest.fixture
def create_test_file():
    test_file_name = 'test.csv'
    dir_path = os.path.dirname(os.path.realpath(__file__))
    test_csv_file_path = dir_path + '/' + test_file_name

    def _create_test_file(field_names, list_of_rows):
        with open(test_csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names, delimiter=',', quotechar='"')
            writer.writeheader()
            for row in list_of_rows:
                writer.writerow(row)
        return test_csv_file_path

    yield _create_test_file

    os.unlink(test_csv_file_path)


@pytest.fixture
def client(create_test_file):
    record_1 = {'id': 1, 'recipe_cuisine': 'british'}
    record_3 = {'id': 2, 'recipe_cuisine': 'nothello'}
    record_5 = {'id': 3, 'recipe_cuisine': 'british'}
    record_2 = {'id': 4, 'recipe_cuisine': 'british'}
    record_4 = {'id': 5, 'recipe_cuisine': 'british'}
    file_path = create_test_file(['id', 'recipe_cuisine'], [record_1, record_2, record_3, record_4, record_5])

    app = create_app({'RECIPE_DATA_FILE_PATH': file_path, 'PAGINATION_LIMIT': 2})
    app.config['TESTING'] = True
    client = app.test_client()

    yield client


def test_a_user_can_retrieve_a_retrieve_a_paginated_list_of_recipes(client):
    query = '?recipe_cuisine=british'

    response = client.get('/recipes' + query)

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2

    for record in data['data']:
        assert record['recipe_cuisine'] == 'british'


def test_a_user_can_get_a_page_of_recipes(client):
    query = '?recipe_cuisine=british'

    response = client.get('/recipes/show/2' + query)

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2

    for record in data['data']:
        assert record['recipe_cuisine'] == 'british'


def test_a_user_can_get_a_recipe_by_id(client):
    response = client.get('/recipes/2')

    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == 2


def test_a_user_can_update_a_recipe_by_id_and_returns_correct_value(client):
    new_recipe_cuisine = 'new_recipe_cuisine'
    response = client.patch('/recipes/2', json=dict(recipe_cuisine=new_recipe_cuisine))

    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == 2
    assert data['recipe_cuisine'] == new_recipe_cuisine


def test_a_user_can_store_a_new_recipe(client):
    response = client.post('/recipes', json=dict(carbs_grams=2, recipe_cuisine='asian'))

    data = json.loads(response.get_data(as_text=True))

    assert data['id'] == 6
    assert data['recipe_cuisine'] == 'asian'
    assert data['carbs_grams'] == 2

