import os
from stat import S_IREAD, S_IRGRP, S_IROTH
import sys

def err_exit():
    sys.exit(1)

def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        err_exit()

    return env_value

def is_file_writable(file_name):
    if os.access(file_name, os.W_OK):
        return True

    return False

def mark_file_readonly(file_name):
    print("Marking %s as readonly!" % (file_name))
    # os.chmod(file_name, 444)
    os.system("chmod 0444 %s" % (file_name))

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

if __name__ == "__main__":
    tickets_dir = get_param(1)

    if tickets_dir is None:
        print("usage: cron_mark_note_tickets_ro.py <tickets-dir>")
        err_exit()

    files = os.listdir(tickets_dir)
    files = [a for a in files if not a.startswith("HW-")]

    for file in files:
        file_path = os.path.join(tickets_dir, file)
        if is_file_writable(file_path):
            mark_file_readonly(file_path)
        else:
            print("The file [%s] is already readonly" % file_path)
