import json
import os
import re
import sys
import uuid
from datetime import datetime, timedelta
import common_utils
from pathlib import Path
import system_config_reader


def load_json_files(json_files):
    data = []

    for json_file in json_files:
        full_path = os.path.join(get_alarms_directory(), json_file)
        # print("Attempting to load: " + json_file)
        data.append(json.loads(common_utils.read_file_contents(full_path)))

    return data


DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def date_to_string(targetDateTime):
    return targetDateTime.strftime(DATE_FORMAT)


def string_to_date(dateInString):
    return datetime.strptime(dateInString, DATE_FORMAT)


def generate_new_id():
    alarms_directory = get_alarms_directory()
    filtered_list = [int(f[:-5]) for f in os.listdir(alarms_directory) if
                     (os.path.isfile(os.path.join(alarms_directory, f)) and f.endswith(".json") and f[:-5].isdigit())]

    if len(filtered_list) < 1:
        return "1"

    next_number = max(filtered_list) + 1
    return str(next_number)

    # while True:
    #     small_uuid = str(uuid.uuid4())[:4]
    #     if not alarm_with_id_exists(small_uuid):
    #         return small_uuid


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
notifications_time: []
"""

ALARM_CREATED_AT = "created_at"
ALARM_TRIGGER_AT = "created_at"
ALARM_TITLE = "title"
ALARM_ID = "id"
ALARM_STATUS = "status"
ALARM_NOTIFICATION_TIMES = "notification_times"

ALARM_STATUS_ACTIVE = "active"
ALARM_STATUS_CLOSED = "closed"


def create_alarm_json(alarm_time, alarm_title):
    return {
        ALARM_CREATED_AT: date_to_string(datetime.now()),
        ALARM_TRIGGER_AT: date_to_string(alarm_time),
        ALARM_TITLE: alarm_title,
        ALARM_ID: generate_new_id(),
        ALARM_STATUS: ALARM_STATUS_ACTIVE,
        ALARM_NOTIFICATION_TIMES: []
    }


# def alarm_with_id_exists(id):
#     file = get_file_path_from_id(id)
#     return os.path.isfile(file)


def get_file_path_from_id(alarm_id):
    return os.path.join(get_alarms_directory(), alarm_id + ".json")


def create_alarm(alarm_time, alarm_title):
    alarm_data = create_alarm_json(alarm_time, alarm_title)
    alarm_id = alarm_data[ALARM_ID]
    save_alarm(alarm_data)
    print("Successfully created: " + alarm_id)


def create_in_alarm(params, arg1, arg2):
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
    create_alarm(alarm_time, " ".join(params[1:]))


def create_at_alarm(params, arg1, arg2):
    if arg1 is None:
        print("Invalid time specified")
        sys.exit(1)

    if arg2 is None:
        print("Alarm title is required")
        sys.exit(1)

    arg1 = arg1.replace(".", ":").replace("-", ":")
    parts = arg1.split(":")
    if len(parts) < 1:
        raise Exception("Format expected like 15.40")

    hours = int(parts[0])
    minutes = int(parts[1]) if len(parts) == 2 else 0

    alarm_time = datetime.now().replace(hour=hours, minute=minutes)
    current_time = datetime.now()

    if alarm_time < current_time:
        alarm_time = alarm_time + timedelta(hours=24)

    create_alarm(alarm_time, " ".join(params[1:]))


def delete_alarm(params, arg1, arg2):
    if arg1 is None:
        print("Invalid id specified")
        sys.exit(1)

    full_path = get_file_path_from_id(arg1)
    file_exists = os.path.isfile(full_path)
    if file_exists:
        os.remove(full_path)
    else:
        print("No such alarm: " + full_path)


def save_alarm(alarm_data):
    alarm_id = alarm_data[ALARM_ID]
    file_path = get_file_path_from_id(alarm_id)
    common_utils.write_to_file(file_path, json.dumps(alarm_data, indent=4))
    print("Successfully persisted alarm: " + alarm_id)


def load_alarm(alarm_id):
    if alarm_id is None:
        print("Invalid alarm id supplied: " + alarm_id)
        raise Exception("Invalid alarm id supplied: " + alarm_id)

    full_path = get_file_path_from_id(alarm_id)
    file_exists = os.path.isfile(full_path)
    if not file_exists:
        print("No such alarm exists: " + alarm_id)
        raise Exception("No such alarm exists: " + alarm_id)

    str_content = common_utils.read_file_contents(full_path)
    return json.loads(str_content)


def close_alarm(params, arg1, arg2):
    alarm_data = load_alarm(arg1)
    alarm_data[ALARM_STATUS] = ALARM_STATUS_CLOSED
    save_alarm(alarm_data)


def list_alarms(params, arg1, arg2):
    alarms_on_disk = get_all_alarms()

    show_all = True if arg1 == "-a" else False

    disp = "%s :: %s :: %s :: %s" % ("ID".ljust(10), "Action".ljust(50), "Status".ljust(20), "Num Notified".ljust(10))
    print("-" * 104)
    print(disp)
    print("-" * 104)

    total_active = 0
    total_closed = 0

    for alarm_on_disk in alarms_on_disk:
        num_notifications = len(alarm_on_disk[ALARM_NOTIFICATION_TIMES])
        alarm_id = alarm_on_disk[ALARM_ID]
        display_name = alarm_on_disk[ALARM_TITLE][:45]
        alarm_status = alarm_on_disk[ALARM_STATUS]
        alarm_is_active = True if (alarm_status == ALARM_STATUS_ACTIVE and num_notifications < 2) else False

        if alarm_is_active:
            total_active = total_active + 1
        else:
            total_closed = total_closed + 1

        if alarm_is_active or show_all:
            disp = "%s :: %s :: %s :: %s" % (alarm_id.ljust(10), display_name.ljust(50), alarm_status.ljust(20), str(num_notifications).ljust(10))
            print(disp)

    print("-" * 104)
    print("Total Active: " + str(total_active))
    print("Total Closed: " + str(total_closed))
    print("-" * 104)


def get_alarms_directory():
    return system_config_reader.get_config('REMINDERS_DROP_DIR')


def get_all_alarms():
    alarms_directory = get_alarms_directory()
    json_files = [f for f in os.listdir(alarms_directory) if
                  (os.path.isfile(os.path.join(alarms_directory, f)) and f.endswith(".json"))]

    return load_json_files(json_files)


def check_whether_alarm_needs_to_be_triggered(alarm_data):
    alarm_id = alarm_data[ALARM_ID]
    if alarm_data[ALARM_STATUS] == ALARM_STATUS_CLOSED:
        print("alarm already closed: " + alarm_id)
        return False

    if len(alarm_data[ALARM_NOTIFICATION_TIMES]) > 2:
        print("alarm notified more than twice: " + alarm_id)
        return False

    if len(alarm_data[ALARM_NOTIFICATION_TIMES]) > 0:
        last_notification_time_text = alarm_data[ALARM_NOTIFICATION_TIMES][-1]
        last_notification_time = string_to_date(last_notification_time_text)
        current_time = datetime.now()
        snooze_period = last_notification_time + timedelta(minutes=30)
        if current_time > snooze_period:
            print("Snooze period complete: " + alarm_data[ALARM_ID])
            return True
        else:
            print("Snooze period not complete yet: " + alarm_data[ALARM_ID])
            return False

    trigger_at = string_to_date(alarm_data[ALARM_TRIGGER_AT])
    current_time = datetime.now()

    if trigger_at >= current_time:
        print("time not arrived yet: " + alarm_id)
        return False

    print("Yes can be triggered: " + alarm_id)
    return True


COMMAND_SYNTAX = '/usr/local/bin/terminal-notifier -title "%s" -subtitle "%s" -message "%s" -execute \'%s %s close %s\''


def fire_alarm(alarm_data):
    python_exec_path = system_config_reader.get_config("PYTHON_EXEC_PATH")
    full_path_of_current_file = os.path.abspath(__file__)
    title = alarm_data[ALARM_TITLE]
    command = COMMAND_SYNTAX % (
    title, "Click to Close (%s)" % alarm_data[ALARM_ID], "Reminder", python_exec_path, full_path_of_current_file, alarm_data[ALARM_ID])
    print("Executing: " + command)
    os.system(command)
    notification_time = date_to_string(datetime.now())
    alarm_data[ALARM_NOTIFICATION_TIMES].append(notification_time)
    save_alarm(alarm_data)


def bot_notify(params, arg1, arg2):
    active_alarms = []
    alarms_on_disk = get_all_alarms()

    for alarm_on_disk in alarms_on_disk:
        alarm_needs_to_be_triggered = check_whether_alarm_needs_to_be_triggered(alarm_on_disk)
        if alarm_needs_to_be_triggered:
            active_alarms.append(alarm_on_disk)

    if len(active_alarms) < 1:
        return

    for active_alarm in active_alarms:
        fire_alarm(active_alarm)


def display_primary_operations(primary_operations):
    primary_operation_codes = [x['code'] for x in primary_operations]
    print("usage: :: a [%s]" % (",".join(primary_operation_codes)))
    for cmd in primary_operations:
        print("\t\t%s \t\t[%s]" % (cmd['code'], cmd['desc']))


if __name__ == "__main__":
    common_credentials_file_path = os.path.join(str(Path.home()), ".common.creds.json")

    primary_operations = [
        get_cmd("in", "Create reminder in [10min, 10m, 1h, 5h, 6hours, 11hour].", create_in_alarm),
        get_cmd("at", "Create reminder in 10.45 am|pm.", create_at_alarm),
        get_cmd("delete", "delete alarms", delete_alarm),
        get_cmd("close", "close alarms", close_alarm),
        get_cmd("list", "list alarms", list_alarms),
        get_cmd("bot_notify", "bot notify", bot_notify)]
    # get_cmd("display", "Save head commit & Open in editor.", display_alarms)]
    # get_cmd("bot_notify", "Should be used by cron/bot to check and display notification if required.", notify_if_required)]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = common_utils.get_param(1)
    if mode is None:
        list_alarms(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))
        common_utils.err_exit()

    if mode not in primary_operation_codes:
        display_primary_operations(primary_operations)
        common_utils.err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']

    fn(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))
