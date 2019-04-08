import csv
import os
import pytest
from app import create_app
import json

test_file_name = 'test.csv'
dir_path = os.path.dirname(os.path.realpath(__file__))
test_csv_file_path = dir_path + '/' + test_file_name
record_1 = {'id': 1, 'recipe_cuisine': 'british', 'average_rating': 3, 'rating_count': 2}
record_2 = {'id': 2, 'recipe_cuisine': 'nothllo', 'average_rating': 3, 'rating_count': 2}
record_3 = {'id': 3, 'recipe_cuisine': 'british', 'average_rating': 3, 'rating_count': 2}
record_4 = {'id': 4, 'recipe_cuisine': 'british', 'average_rating': 3, 'rating_count': 2}
record_5 = {'id': 5, 'recipe_cuisine': 'british', 'average_rating': 3, 'rating_count': 2}


@pytest.fixture
def create_test_file():
    def _create_test_file(test_csv_file_path, field_names, list_of_rows):
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
    file_path = create_test_file(test_csv_file_path, ['id', 'recipe_cuisine', 'average_rating', 'rating_count'],
                                 [record_1, record_2, record_3, record_4, record_5])

    app = create_app({'RECIPE_DATA_FILE_PATH': file_path, 'PAGINATION_LIMIT': 2})
    app.config['TESTING'] = True

    client = app.test_client()

    yield client


def test_a_user_can_retrieve_a_paginated_list_of_recipes_without_a_filter(client):
    response = client.get('/recipes')

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2
    assert 'nextPage' in data['pagination']
    assert 'prevPage' not in data['pagination']


def test_a_user_can_retrieve_a_paginated_list_of_recipes_with_filter(client):
    query = '?recipe_cuisine=british'

    response = client.get('/recipes' + query)

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2

    for record in data['data']:
        assert record['recipe_cuisine'] == 'british'


def test_it_can_retrieve_more_page_limit_with_per_page(client):
    query = '?per_page=4'

    response = client.get('/recipes' + query)

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 4


def test_a_user_can_filter_by_recipe_cuisine(client):
    query = '?recipe_cuisine=british'

    response = client.get('/recipes' + query)

    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2

    for record in data['data']:
        assert record['recipe_cuisine'] == 'british'


def test_a_user_can_see_the_second_page_of_pagination(client):
    response = client.get('/recipes/page/2?per_page=2')
    print(response.get_data(as_text=True))
    data = json.loads(response.get_data(as_text=True))

    assert len(data['data']) == 2
    assert 'nextPage' in data['pagination']
    assert 'prevPage' in data['pagination']


def test_a_user_can_get_a_recipe_by_id(client):
    response = client.get('/recipes/2')

    data = json.loads(response.get_data(as_text=True))
    for key, value in record_2.items():

        assert data[key] == value
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
    assert response.status_code == 201


def test_a_user_can_add_a_rating_and_returns_recipe_with_new_average_rating(client):
    avg_rating = 3
    rating_count = 2
    response = client.post('/recipes/2/ratings', json=dict(rating=5))

    rating_total = avg_rating * rating_count

    rating_total = rating_total + 5
    expected_rating_count = rating_count + 1
    expected_average_rating = rating_total / expected_rating_count

    data = json.loads(response.get_data(as_text=True))

    assert data['average_rating'] == expected_average_rating
    assert data['rating_count'] == expected_rating_count


def test_a_user_cannot_add_a_rating_over_5_by_returning_403(client):
    response = client.post('/recipes/2/ratings', json=dict(rating=6))

    assert response.status_code == 403


def test_a_user_cannot_add_a_rating_under_0_by_returning_403(client):
    response = client.post('/recipes/2/ratings', json=dict(rating=-1))

    assert response.status_code == 403


def test_a_user_cannot_add_send_an_empty_rating(client):
    response = client.post('/recipes/2/ratings')

    assert response.status_code == 400
