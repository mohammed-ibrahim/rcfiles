import sys
import os
import subprocess


def err_exit():
    sys.exit(1)

def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        err_exit()

    return env_value

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def fetch_file_names_in_dir(dir):
    files = os.listdir(dir)
    return files

def run_process_and_get_output(command_list, exit_on_failure=False):
    print("Executing ::: %s" % " ".join(command_list))
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        err_exit()

    return out

def s_run_process_and_get_output(s_cmd, exit_on_failure=False):
    return run_process_and_get_output(s_cmd.split(" "), exit_on_failure)

def unlock_file(file_path):
    s_run_process_and_get_output("chmod 0666 %s" % file_path)

def interactive_unlock(files, tickets_directory, pattern):
    map = {}
    index = 1
    for file in files:
        if pattern is None or pattern in file:
            map[str(index)] = file
            index = index + 1

    if len(map) < 1:
        print("pattern doesn't match any file: %s" % pattern)
        err_exit()

    for i in range(index-1):
        idx = str(i+1)
        print("%s - %s" % (idx, map[idx]))

    user_input = input("Please select file number: ")
    user_input = user_input.strip()
    print("Selected: " + user_input)

    if user_input not in map:
        print("Option %s not mentioned in the list above" % user_input)
        err_exit()
    else:
        unlock_file(os.path.join(tickets_directory, map[user_input]))
    # TODO: start from here.

if __name__ == "__main__":
    tickets_directory = pull_env_var('TICKETS_DIR')
    param = get_param(1)

    files_in_ticket_dir = fetch_file_names_in_dir(tickets_directory)

    if param is not None:
        # full path is mentioned
        if os.path.isfile(param):
            unlock_file(param)
        elif param in files_in_ticket_dir:
            unlock_file(os.path.join(tickets_directory, param))
        else:
            interactive_unlock(files_in_ticket_dir, tickets_directory, param)
    else:
        interactive_unlock(files_in_ticket_dir, tickets_directory, None)
