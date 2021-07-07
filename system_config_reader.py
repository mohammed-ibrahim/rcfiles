from pathlib import Path
import os
import sys
import common_utils

GLOBAL_MAP = None


def load_global_map():
    print("Loading global map")
    global GLOBAL_MAP
    GLOBAL_MAP = {}

    bash_file_path = os.path.join(str(Path.home()), ".bash_profile")
    file_contents = common_utils.read_file_contents(bash_file_path)
    lines = file_contents.split("\n")
    filtered = [f for f in lines if f.startswith("export ")]

    for line in filtered:
        (key, value) = parse_line(line)
        GLOBAL_MAP[key] = value


def parse_line(line):
    line = line.replace("export ", "")
    parts = line.split("=")
    key = parts[0]
    value = parts[1]

    if value.startswith("'") and value.endswith("'"):
        value = value[1:-1]

    if value.startswith('"') and value.endswith('"'):
        value = value[1:-1]

    return key, value


def get_config(name):
    global GLOBAL_MAP

    if GLOBAL_MAP is None:
        load_global_map()

    if name in GLOBAL_MAP:
        return GLOBAL_MAP[name]

    print("Config: %s not found." % name)
    sys.exit(1)


if __name__ == "__main__":
    print(get_config('REMINDERS_DROP_DIR'))