from math import ceil
from typing import Optional, List, Any


class MemTable:
    query: List[Optional[Any]]
    memory_list: dict

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
