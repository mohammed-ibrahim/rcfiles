import json
import common_utils
import os
from pathlib import Path
from datetime import datetime, timedelta
import requests
from requests.exceptions import InvalidURL, MissingSchema

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

FIELD_WATCHER_ID = "id"
FIELD_CREATED_AT = "created_at"
FIELD_URL = "url"
FIELD_NOTIFICATION_TIMES = "notification_times"
FIELD_STATUS = "status"
FIELD_REASON = "reason"

FIELD_VALUE_FOR_STATUS_CREATED = "created"
FIELD_VALUE_FOR_STATUS_CLOSED = "closed"
FIELD_VALUE_FOR_REASON_EXPIRED = "Watcher time expired"


def create_watcher(params, arg1, arg2):
    if arg1 is None:
        print("Please provide correct url to watch")
        common_utils.err_exit()

    url = arg1
    print("Creating watcher for: " + url)
    data = {
        FIELD_WATCHER_ID: generate_new_id(),
        FIELD_CREATED_AT: date_to_string(datetime.now()),
        FIELD_URL: url,
        FIELD_STATUS: FIELD_VALUE_FOR_STATUS_CREATED
    }

    save_watcher(data)


def get_complete_watch_list():
    watchers_directory = get_watcher_directory()
    json_files = [f for f in os.listdir(watchers_directory) if
                  (os.path.isfile(os.path.join(watchers_directory, f)) and f.endswith(".json"))]

    files_list = [os.path.join(watchers_directory, x) for x in json_files]
    return common_utils.load_json_files(files_list)


def whether_watcher_time_expired(watcher_data):
    created_at_string_format = watcher_data[FIELD_CREATED_AT]
    created_at_date = string_to_date(created_at_string_format)
    watcher_expiry_time = created_at_date + timedelta(hours=5)
    current_time = datetime.now()

    if current_time > watcher_expiry_time:
        return False

    return True


def whether_watcher_is_active(watcher_data):
    status = watcher_data[FIELD_STATUS]

    if status in [FIELD_VALUE_FOR_STATUS_CLOSED]:
        return False

    return whether_watcher_time_expired(watcher_data)


WATCHER_ACTION_DO_NOTHING = "nothing"
WATCHER_ACTION_DO_KEEP_POLLING = "keepPolling"
WATCHER_ACTION_DO_NOTIFY_SUCCESS = "notifySuccess"
WATCHER_ACTION_DO_NOTIFY_FAILURE = "notifyFailure"


def get_notification_body(watcher_data, reason):
    # TODO: return notification body
    return None


def fetch_job_status(watcher_data):
    url = watcher_data[FIELD_URL]
    json_api_url = url + "/api/json"

    try:
        response = requests.get(json_api_url)
        if response.status_code != 200:
            # Stopped here
    except (InvalidURL, MissingSchema) as e:
        # Stopped here


def determine_watcher_action(watcher_data):
    status = watcher_data[FIELD_STATUS]

    if status in [FIELD_VALUE_FOR_STATUS_CLOSED]:
        return None

    if status == FIELD_VALUE_FOR_STATUS_CREATED:
        expired = whether_watcher_time_expired(watcher_data)

        if expired:
            watcher_data[FIELD_STATUS] = FIELD_VALUE_FOR_STATUS_CLOSED
            watcher_data[FIELD_REASON] = FIELD_VALUE_FOR_REASON_EXPIRED
            save_watcher(watcher_data)
            return get_notification_body(watcher_data, FIELD_VALUE_FOR_REASON_EXPIRED)
        else:
            job_status_result = fetch_job_status(watcher_data)

    # TODO: Stopped here


def list_watchers(params, arg1, arg2):
    watchers_list = get_complete_watch_list()
    show_all = True if arg1 == "-a" else False

    disp = "%s :: %s :: %s :: %s" % ("ID".ljust(10), "Url".ljust(50), "Status".ljust(20), "Num Notified".ljust(10))
    print("-" * 104)
    print(disp)
    print("-" * 104)

    total_active = 0
    total_closed = 0

    for watcher_item in watchers_list:
        num_notifications = 0

        if FIELD_NOTIFICATION_TIMES in watcher_item:
            num_notifications = len(watcher_item[FIELD_NOTIFICATION_TIMES])

        watcher_id = watcher_item[FIELD_WATCHER_ID]
        url = watcher_item[FIELD_URL][:45]
        watcher_status = watcher_item[FIELD_STATUS]
        watcher_is_active = whether_watcher_is_active(watcher_item)

        if watcher_is_active:
            total_active = total_active + 1
        else:
            total_closed = total_closed + 1

        if watcher_is_active or show_all:
            disp = "%s :: %s :: %s :: %s" % (
                watcher_id.ljust(10), url.ljust(50), watcher_status.ljust(20), str(num_notifications).ljust(10))
            print(disp)

    print("-" * 104)
    print("Total Active: " + str(total_active))
    print("Total Closed: " + str(total_closed))
    print("-" * 104)


def bot_notify(params, arg1, arg2):
    watchers_list = get_complete_watch_list()

    for watcher_item in watchers_list:
        watcher_is_active = whether_watcher_is_active(watcher_item)
    return None


def get_file_path_from_id(watcher_id):
    return os.path.join(get_watcher_directory(), watcher_id + ".json")


def save_watcher(watcher_data):
    watcher_id = watcher_data[FIELD_WATCHER_ID]
    file_path = get_file_path_from_id(watcher_id)
    common_utils.write_to_file(file_path, json.dumps(watcher_data, indent=4))
    print("Successfully persisted watcher: " + watcher_id)


def get_watcher_directory():
    return CONFIG_DATA['WATCHER_DROP_DIR']


def generate_new_id():
    watcher_directory = get_watcher_directory()
    filtered_list = [int(f[:-5]) for f in os.listdir(watcher_directory) if
                     (os.path.isfile(os.path.join(watcher_directory, f)) and f.endswith(".json") and f[:-5].isdigit())]

    if len(filtered_list) < 1:
        return "1"

    next_number = max(filtered_list) + 1
    return str(next_number)


def date_to_string(targetDateTime):
    return targetDateTime.strftime(DATE_FORMAT)


def string_to_date(dateInString):
    return datetime.strptime(dateInString, DATE_FORMAT)


def get_cmd(code, desc, fnc):
    return {
        "code": code,
        "desc": desc,
        "fnc": fnc,
    }


def display_primary_operations(primary_operations):
    primary_operation_codes = [x['code'] for x in primary_operations]
    print("usage: :: a [%s]" % (",".join(primary_operation_codes)))
    for cmd in primary_operations:
        print("\t\t%s \t\t[%s]" % (cmd['code'], cmd['desc']))


if __name__ == "__main__":
    common_credentials_file_path = os.path.join(str(Path.home()), ".common.creds.json")
    config_data_content = common_utils.read_file_contents(common_credentials_file_path)
    CONFIG_DATA = json.loads(config_data_content)

    primary_operations = [
        get_cmd("c", "Create jenkins watcher", create_watcher),
        get_cmd("bot_notify", "bot notify", bot_notify),
        get_cmd("list", "list", list_watchers)]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = common_utils.get_param(1)
    if mode is None:
        list_watchers(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))
        common_utils.err_exit()

    if mode not in primary_operation_codes:
        display_primary_operations(primary_operations)
        common_utils.err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']

    fn(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))
