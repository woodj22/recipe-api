import csv
import os
from database.filetypes import csv_loader
import pytest
from database.mem_table import MemTable


@pytest.fixture
def create_test_file():
    test_csv_file_path = 'test.csv'

    def _create_test_file(field_names, list_of_rows):
        with open(test_csv_file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=field_names, delimiter=',', quotechar='"')
            writer.writeheader()
            for row in list_of_rows:
                writer.writerow(row)
        return test_csv_file_path

    yield _create_test_file

    os.unlink(test_csv_file_path)


def test_csv_loader_can_load_a_csv_into_memory(create_test_file):
    field_names = ['bullet_1', 'bullet_2']
    actual_dict = {'bullet_1': 'hello', 'bullet_2': 'egd'}
    file_path = create_test_file(field_names, [actual_dict])

    mem = csv_loader(file_path)

    assert list(actual_dict.values()) == list(mem[1].values())


def test_mem_table_can_retrieve_a_record_by_id(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'esdsgd'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)

    recipes = MemTable(memory)

    result = recipes.find(1)
    assert list(record_1.values()) == list(result.values())


def test_mem_table_can_retrieve_an_indexed_list_of_records(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'esdsgd'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)

    recipes = MemTable(memory)

    result = recipes.list()

    assert [record_1, record_2, record_3] == result


def test_mem_table_can_store_new_record(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'esdsgd'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)
    new_record = {'bullet_2': 'new_test'}
    recipes = MemTable(memory)
    recipes.store(new_record)

    assert new_record in recipes.memory_list


def test_mem_table_can_filter_by_attributes_and_sets_it_to_the_query_global_variable(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'test_filtered'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)
    recipes = MemTable(memory)
    mem = recipes.filter_by({'bullet_2': 'test_filtered'})

    assert mem is recipes
    assert record_2 in recipes.query


def test_mem_table_can_return_whole_memory_list_if_no_filters_applied(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'test_filtered'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)
    recipes = MemTable(memory)
    mem = recipes.filter_by({})

    assert mem is recipes
    assert all(x in [record_1, record_2, record_3] for x in recipes.query)


def test_mem_table_can_update_a_single_record(create_test_file):
    field_names = ['id', 'bullet_2']
    record_1 = {'id': 1, 'bullet_2': 'egd'}
    record_2 = {'id': 2, 'bullet_2': 'test_filtered'}
    record_3 = {'id': 3, 'bullet_2': 'versdfgv'}
    file_path = create_test_file(field_names, [record_1, record_2, record_3])

    memory = csv_loader(file_path)
    recipes = MemTable(memory)

    new_record = {'id': 2, 'bullet_2': 'new-bullet'}

    recipes.update(1, new_record)

    assert recipes.memory_list[1] == new_record
