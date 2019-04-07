from math import ceil
from typing import Optional, List, Any


class MemTable:
    query: List[Optional[Any]]
    memory_list: list

    def __init__(self, memory_list):
        self.memory_list = memory_list[1:]

    def find(self, index):
        return dict(self.memory_list[index])

    def list(self):
        return {'data': self.memory_list}

    def filter_by(self, filters: dict):
        filtered_list = []

        for row in self.memory_list:
            for filter_key, filter_value in filters.items():
                if row is None:
                    print(row)

                if row[filter_key] == filter_value:
                    filtered_list.append(row)
        self.query = filtered_list

        return self

    def paginate(self, page, per_page):
        count = len(self.query)

        if page == 1:
            page_start = 0
            page_end = per_page
        else:
            page_start = page * per_page
            page_end = page_start + per_page

        pagination = Pagination(page, per_page, count)

        paginationDict = {
            'data': self.query[page_start:(page_end)],
            'pagination': {}
        }

        if pagination.has_next:
            paginationDict['pagination']['nextPage'] = 'recipes/page/' + str(page + 1)

        if pagination.has_prev:
            paginationDict['pagination']['prevPage'] = 'recipes/page/' + str(page - 1)

        return paginationDict

    def update(self, index, params: dict):
        new_row = self.find(index)
        for filter_key, filter_value in params.items():
            if filter_key in new_row:
                new_row[filter_key] = filter_value

        self.memory_list[index] = new_row

        return new_row

    def store(self, params: dict):
        id = self._get_next_id()
        params['id'] = id

        self.memory_list.append(params)
        print(self.memory_list)
        return params

    def _get_next_id(self):
        return len(self.memory_list) + 1

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
