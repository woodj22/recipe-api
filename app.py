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

    recipes = MemTable(memory)

    @app.route('/recipes', defaults={'page': 1})
    @app.route('/recipes/page/<int:page>')
    def index(page):
        cuisine = request.args.get('recipe_cuisine')
        filtered_recipes = recipes.filter_by({'recipe_cuisine': cuisine}).paginate(page, per_page)
        if not filtered_recipes and page != 1:
            abort(404)

        return json.dumps(filtered_recipes)

    return app



class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
                    (num > self.page - left_current - 1 and \
                     num < self.page + right_current) or \
                    num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num
