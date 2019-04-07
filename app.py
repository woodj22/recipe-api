from math import ceil
from flask import Flask, abort, render_template
from flask import request

from database.filetypes import csv_loader
from database.mem_table import MemTable
import json


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    file_path = app.config['RECIPE_DATA_FILE_PATH']
    per_page = int(app.config['PAGINATION_LIMIT'])
    memory = csv_loader(file_path)

    recipe_model = MemTable(memory)

    @app.route('/recipes', defaults={'page': 1})
    @app.route('/recipes/page/<int:page>')
    def index(page):
        cuisine = request.args.get('recipe_cuisine')
        filtered_recipes = recipe_model.filter_by({'recipe_cuisine': cuisine}).paginate(page, per_page)

        if not filtered_recipes and page != 1:
            abort(404)

        return json.dumps(filtered_recipes)

    @app.route('/recipes/<int:id>', methods=['get'])
    def show(id):
        recipe = recipe_model.find(id)
        if not recipe:
            abort(404)
        return json.dumps(recipe)

    @app.route('/recipes/<int:id>', methods=['patch'])
    def update(id):
        updated_recipe = recipe_model.update(id, request.get_json())
        if not updated_recipe:
            abort(404)
        return json.dumps(updated_recipe)

    @app.route('/recipes', methods=['post'])
    def create():
        params = request.get_json()
        return json.dumps(recipe_model.store(params))

    @app.route('/recipes/<int:id>/ratings', methods=['put'])
    def update_rating(id):
        existing_model = recipe_model.find(id)
        rating_count = existing_model['rating_count']

        average_rating = _calculate_average_rating(existing_model['average_rating'], existing_model['rating_count'],
                                                   request.get_json()['rating'])

        new_params = {'average_rating': average_rating, 'rating_count': rating_count + 1}

        updated_recipe = recipe_model.update(id, new_params)
        return json.dumps(updated_recipe)

    def _calculate_average_rating(current_avg_rating, current_rating_count, new_rating):
        rating_total = (current_avg_rating * current_rating_count) + new_rating

        average_rating = rating_total / (current_rating_count + 1)

        return average_rating

    return app
