import csv


def csv_loader(input_path) -> list:
    with open(input_path, newline='') as csvfile:
        memory = csv.DictReader(csvfile, delimiter=',')
        memory_list = [memory.fieldnames]
        for row in memory:  # read a row as {column1: value1, column2: value2,...}
            typed_value = {}
            for (k, v) in row.items():  # go over each column name and value
                try:
                    typed_value[k] = int(v)
                except ValueError:
                    typed_value[k] = v

            memory_list.append(typed_value)

    return memory_list
