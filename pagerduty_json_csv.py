import csv
import json
import sys
import os
import uuid
import pyperclip


def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

def get_alarm_arn_if_present(i):

    if 'first_trigger_log_entry' in i:
        first_log_entry = i['first_trigger_log_entry']
        if 'channel' in first_log_entry:
            channel = first_log_entry['channel']
            if 'details' in channel and 'AlarmArn' in channel['details']:
                return channel['details']['AlarmArn']

    return "not found"

def get_row_from_incident(i):
    title = i['title']
    service = i['service']['summary']
    created_at = i['created_at']
    assigned_via = i['assigned_via']
    id = i['id']
    last_update_by = i['last_status_change_by']['summary']
    alarm_arn = get_alarm_arn_if_present(i)

    return [title, service, created_at, assigned_via, id, last_update_by, alarm_arn]


def write_json_file_entries_to_csv(full_json_file_path, csv_writer):
    string_json = read_file_contents(full_json_file_path)
    data = json.loads(string_json)

    incidents = data['incidents']

    if len(incidents) < 1:
        return

    for i in incidents:
        row = get_row_from_incident(i)
        csv_writer.writerow(row)


def process_directory(directory):
    json_files = [f for f in os.listdir(directory) if
                  (os.path.isfile(os.path.join(directory, f)) and f.endswith(".json"))]
    print(json_files)

    csv_file_name = os.path.join(directory, str(uuid.uuid4()) + ".csv")
    with open(csv_file_name, 'w') as writer_file_handle:
        csv_writer = csv.writer(writer_file_handle)

        for json_file in json_files:
            full_json_file_path = os.path.join(directory, json_file)
            write_json_file_entries_to_csv(full_json_file_path, csv_writer)

    cmd = 'open -a "Microsoft Excel" %s' % csv_file_name
    pyperclip.copy(cmd)
    print(cmd + " :: copied to clipboard")

if __name__ == "__main__":
    directory = get_param(1)

    if directory is None:
        print("This operation requires directory")
        sys.exit(1)

    process_directory(directory)
