import csv
import sys


# def group_data(data, headers, group_by_column):
#     grouped = {}
#     total_rows = len(data)
#     for row in data:
#         column_value_index = headers.index(group_by_column)
#         column_value = row[column_value_index]
#         existing_count = grouped.get(column_value, 0)
#         grouped[column_value] = existing_count + 1
#
#     results = []
#     for key,value in grouped:
#         results.append([key, value, getPercentage(total_rows, value)])
#
#     return results

def getPercentage(total, current):
    result = (float(current) * 100.00) / float(total)
    return round(result, 2)

def print_grouped_data(grouped_data):
    for row in grouped_data:
        row_data = list()
        total_columns = len(row)
        for i in range(total_columns-2):
            row_data.append(row[i].ljust(20))

        cardinality = str(row[total_columns - 2]).ljust(5)
        row_data.append(cardinality)
        percentage_text = str(row[total_columns - 1])
        row_data.append(percentage_text)
        print(" | ".join(row_data))

def get_column_values(row, grouping_columns):
    column_values = []
    for column_name in grouping_columns:
        column_value = row[column_name]
        column_values.append(column_value)

    return column_values

def group_csv(csv_file_name, grouping_columns):
    with open(csv_file_name, 'r') as reader_file_handle:
        reader = csv.DictReader(reader_file_handle)

        total_rows = 0
        grouped = {}
        for row in reader:
            total_rows = total_rows + 1
            column_values = get_column_values(row, grouping_columns)
            group_by_key = ".".join(column_values)
            existing_data = grouped.get(group_by_key, {"data": column_values, "count": 0})
            existing_data["count"] = existing_data["count"] + 1
            grouped[group_by_key] = existing_data

        results = []
        for key in grouped:
            value = grouped[key]
            result_row = list(value['data'])
            count = value['count']
            result_row.append(count)
            result_row.append(getPercentage(total_rows, count))
            results.append(result_row)

        print_grouped_data(results)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python csv_group.py file_name.csv column_name")
        sys.exit(1)

    csv_file_name = sys.argv[1]
    group_by_column = sys.argv[2]
    group_csv(csv_file_name, group_by_column.split(","))