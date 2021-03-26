import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta
import common_utils


def load_json_files(drop_directory, json_files):
    data = []

    for json_file in json_files:
        full_path = os.path.join(drop_directory, json_file)
        print("Attempting to load: " + json_file)
        data.append(json.loads(common_utils.read_file_contents(full_path)))

    return data


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def date_to_string(targetDateTime):
    return targetDateTime.strftime(DATE_FORMAT)


def string_to_date(dateInString):
    return datetime.strptime(dateInString, DATE_FORMAT)


def generate_new_id():
    return str(uuid.uuid4())


"""
# TODO:
1. Create in minutes
2. Create in hours
3. Create at
4. List
5. Delete
6. Snooze
7. Notify
8. Update Alarm
9. Add notification addition
"""


def get_cmd(code, desc, fnc):
    return {
        "code": code,
        "desc": desc,
        "fnc": fnc,
    }


def get_first_position_of_alphabets(text):
    result = re.search(r'[a-z]', text, re.I)
    if result is not None:
        return result.start()
    return None


"""
created_at: <date>
trigger_at: <date>
completed: true/false
title: <string>
id: <string>
"""


def create_alarm_json(alarm_time, alarm_title):
    return {
        "created_at": date_to_string(datetime.now()),
        "trigger_at": date_to_string(alarm_time),
        "title": alarm_title,
        "id": str(uuid.uuid4()),
        "status": "active"
    }


def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)


def create_alarm(alarm_time, alarm_title, alarms_directory):
    alarm_data = create_alarm_json(alarm_time, alarm_title)
    alarm_id = alarm_data['id']
    file_path = os.path.join(alarms_directory, alarm_id + ".json")
    write_to_file(file_path, json.dumps(alarm_data, indent=4))
    print("Successfully created: " + alarm_id)


def create_in_alarm(params, arg1, arg2, alarms_directory):
    if arg1 is None:
        print("Invalid time specified")
        sys.exit(1)

    if arg2 is None:
        print("Alarm title is required")
        sys.exit(1)

    arg1 = arg1.lower()
    index = get_first_position_of_alphabets(arg1)
    if index is None or index == 0:
        raise Exception("Invalid arg: " + arg1)

    number_part = int(arg1[:index])
    text_part = arg1[index:]
    # print(number_part, text_part)

    minutes_delta = 0
    if text_part[0] == 'm':
        minutes_delta = number_part
    elif text_part[0] == 'h':
        minutes_delta = number_part * 60
    else:
        raise Exception("Invalid format: it should start either with 'h' or 'm'")

    # print(minutes_delta)
    alarm_time = datetime.now() + timedelta(minutes=minutes_delta)
    create_alarm(alarm_time, " ".join(params[1:]), alarms_directory)


def display_primary_operations(primary_operations):
    primary_operation_codes = [x['code'] for x in primary_operations]
    print("usage: :: a [%s]" % (",".join(primary_operation_codes)))
    for cmd in primary_operations:
        print("\t\t%s \t\t[%s]" % (cmd['code'], cmd['desc']))


if __name__ == "__main__":
    reminder_files_directory = common_utils.pull_env_var("REMINDERS_DROP_DIR")

    json_files = [f for f in os.listdir(reminder_files_directory) if
                  (os.path.isfile(os.path.join(reminder_files_directory, f)) and f.endswith(".json"))]

    alarm_jsons = load_json_files(reminder_files_directory, json_files)

    primary_operations = [
        get_cmd("in", "Create reminder in [10min, 10m, 1h, 5h, 6hours, 11hour].", create_in_alarm)]
    # get_cmd("at", "Create reminder in 10.45 am|pm.", create_at_alarm),
    # get_cmd("delete", "delete alarms", delete_alarms),
    # get_cmd("display", "Save head commit & Open in editor.", display_alarms),
    # get_cmd("bot_notify", "Should be used by cron/bot to check and display notification if required.", notify_if_required)]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = common_utils.get_param(1)
    if mode is None or mode not in primary_operation_codes:
        display_primary_operations(primary_operations)
        common_utils.err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']

    fn(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3), reminder_files_directory)
