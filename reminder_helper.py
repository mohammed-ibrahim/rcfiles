import json
import os
import sys


def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        sys.exit(1)

    return env_value

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

def load_json_files(drop_directory, json_files):

    data = []

    for json_file in json_files:
        full_path = os.path.join(drop_directory, json_file)
        print("Attempting to load: " + json_file)
        data.append(json.loads(read_file_contents(full_path)))

    return data

if __name__ == "__main__":
    reminder_files_directory = pull_env_var("REMINDERS_DROP_DIR")

    json_files = [f for f in os.listdir(reminder_files_directory) if
                  (os.path.isfile(os.path.join(reminder_files_directory, f)) and f.endswith(".json"))]

    alarm_jsons = load_json_files(reminder_files_directory, json_files)