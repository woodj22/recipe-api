from math import ceil
from flask import Flask, abort, render_template
from flask import request
from flask import Response
from database.filetypes import csv_loader
from database.mem_table import MemTable
import json


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    file_path = app.config['RECIPE_DATA_FILE_PATH']
    default_per_page = int(app.config['PAGINATION_LIMIT'])

    allowed_recipe_filters = ['recipe_cuisine']

    memory = csv_loader(file_path)

    recipe_model = MemTable(memory)

    @app.route('/recipes', defaults={'page': 1})
    @app.route('/recipes/page/<int:page>')
    def index(page):
        per_page = request.args.get('per_page')
        per_page = per_page if per_page is not None else default_per_page

        filters = _recipe_filters(request.args)

        filtered_recipes = recipe_model.filter_by(filters).paginate(page, per_page, 'recipes')

        if not filtered_recipes and page != 1:
            return '', 404

        return json.dumps(filtered_recipes)

    @app.route('/recipes/<int:id>', methods=['get'])
    def show(id):
        recipe = recipe_model.find(id)

        if not recipe:
            return '', 404

        return json.dumps(recipe)

    @app.route('/recipes/<int:id>', methods=['patch'])
    def update(id):
        updated_recipe = recipe_model.update(id, request.get_json())

        if not updated_recipe:
            return '', 404

        return json.dumps(updated_recipe)

    @app.route('/recipes', methods=['post'])
    def create():
        params = request.get_json()

        return json.dumps(recipe_model.store(params)), 201

    @app.route('/recipes/<int:id>/ratings', methods=['put'])
    def update_rating(id):
        existing_model = recipe_model.find(id)
        rating_count = existing_model['rating_count']

        if request.get_json()['rating'] > 5 or request.get_json()['rating'] < 0:
            return '', 403

        average_rating = _calculate_average_rating(existing_model['average_rating'], existing_model['rating_count'],
                                                   request.get_json()['rating'])

        new_params = {'average_rating': average_rating, 'rating_count': rating_count + 1}

        updated_recipe = recipe_model.update(id, new_params)

        return json.dumps(updated_recipe)

    def _calculate_average_rating(current_avg_rating, current_rating_count, new_rating):
        rating_total = (current_avg_rating * current_rating_count) + new_rating

        average_rating = rating_total / (current_rating_count + 1)

        return average_rating

    def _recipe_filters(queries):
        filters = {}
        for v in allowed_recipe_filters:
            if v in queries:
                filters = {v: request.args.get(v)}

        return filters

    return app
