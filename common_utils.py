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


def err_exit():
    sys.exit(1)


def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None


def get_params():
    cmd_list = []
    for i in range(2, len(sys.argv)):
        cmd = sys.argv[i]
        cmd_list.append(cmd)
    return cmd_list


def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)