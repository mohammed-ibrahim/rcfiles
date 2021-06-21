import json
import common_utils
import os
from pathlib import Path
from datetime import datetime, timedelta

DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"

FIELD_WATCHER_ID = "id"
FIELD_CREATED_AT = "created_at"
FIELD_URL = "url"
FIELD_NOTIFICATION_TIMES = "notification_times"
FIELD_STATUS = "status"


FIELD_VALUE_FOR_STATUS_CREATED = "created"
FIELD_VALUE_FOR_STATUS_EXPIRED = "expired"
FIELD_VALUE_FOR_STATUS_CLOSED = "closed"
FIELD_VALUE_FOR_STATUS_INVALID_URL = "invalid_url"


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


def bot_notify(params, arg1, arg2):
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


if __name__ == "__main__":
    common_credentials_file_path = os.path.join(str(Path.home()), ".common.creds.json")
    config_data_content = common_utils.read_file_contents(common_credentials_file_path)
    CONFIG_DATA = json.loads(config_data_content)

    primary_operations = [
        get_cmd("c", "Create jenkins watcher", create_watcher),
        get_cmd("bot_notify", "bot notify", bot_notify)]
    # get_cmd("display", "Save head commit & Open in editor.", display_alarms)]
    # get_cmd("bot_notify", "Should be used by cron/bot to check and display notification if required.", notify_if_required)]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = common_utils.get_param(1)
    if mode is None or mode not in primary_operation_codes:
        # display_primary_operations(primary_operations)
        # list_alarms(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))
        common_utils.err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']

    fn(common_utils.get_params(), common_utils.get_param(2), common_utils.get_param(3))