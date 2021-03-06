import time
from math import ceil
from typing import Optional, List, Any


class MemTable:
    query: List[Optional[Any]]
    memory_list: list

    def __init__(self, memory_list):
        self.memory_list = memory_list

    def find(self, index):
        return dict(self.memory_list[index])

    def list(self):
        return self.memory_list[1:]

    def filter_by(self, filters: dict):
        """
        Filter by values present in dictionary. If the filter variable is empty it will not apply any filters.
        :param filters:
        :return:
        """
        filtered_list = []
        for row in self.memory_list[1:]:
            for filter_key, filter_value in filters.items():
                if row[filter_key] == filter_value:
                    filtered_list.append(row)
                    continue
        if not filters:
            self.query = self.memory_list[1:]
        else:
            self.query = filtered_list
        return self

    def paginate(self, page, per_page, base_url):
        count = len(self.query)

        page_end = (int(page) * int(per_page))
        page_start = (int(page_end) - int(per_page))

        pagination = Pagination(page, per_page, count)

        pagination_dict = {
        'data': self.query[int(page_start):int(page_end)],
        'pagination': {}
        }

        if pagination.has_next:
            pagination_dict['pagination']['nextPage'] = base_url + '/page/' + str(page + 1)

        if pagination.has_prev:
            pagination_dict['pagination']['prevPage'] = base_url + '/page/' + str(page - 1)

        return pagination_dict


    def update(self, index, params: dict):
        new_row = self.find(index)
        for filter_key, filter_value in params.items():
            # if filter_key in new_row:
            new_row[filter_key] = filter_value

        self.memory_list[index] = new_row

        return new_row


    def store(self, params: dict):
        id = self._get_next_id()
        params['id'] = id

        self.memory_list.append(params)

        return params


    def _get_next_id(self):
        return len(self.memory_list)


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
