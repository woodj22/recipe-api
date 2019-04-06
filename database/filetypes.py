import csv


def csv(input_path):
    with open(input_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        print(reader)
        # for row in reader:

            # print(row['first_name'], row['last_name'])


    return 'hello world'
