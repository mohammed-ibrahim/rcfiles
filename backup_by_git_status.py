import sys
import os
import subprocess
import datetime
import time


def run_process_and_get_output(command_list, exit_on_failure=False):
    print("Executing ::: %s" % " ".join(command_list))
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        print("Failed to run the command :: exiting ::: %s" % " ".join(command_list))
        sys.exit(1)

    return out

def s_run_process_and_get_output(s_cmd, exit_on_failure=False):
    return run_process_and_get_output(s_cmd.split(" "), exit_on_failure)

def remove_git_formatting(line):
    line = line.replace("modified:", "").replace("\t", "").replace(" ", "")
    return line

def get_modified_files_from_git_status(process_text):
    lines = [x for x in process_text.split("\n") if "modified:" in x]
    cleared_lines = [remove_git_formatting(g) for g in lines]
    return cleared_lines


if __name__ == "__main__":

    local_directory = os.environ.get('LOCAL_BACKUP_DIR', None)
    if local_directory is None:
        print("LOCAL_BACKUP_DIR is not set")
        sys.exit(1)

    cwd = os.getcwd()
    print("Loading files from :: %s" % cwd)

    process_output = s_run_process_and_get_output("git status", True)
    modified_files_from_git_status = get_modified_files_from_git_status(process_output)

    path_parts = cwd.split("/")
    required_notifier = path_parts.pop().strip()

    if len(required_notifier) == 0:
        required_notifier = "unable-to-fetch-src-folder"

    ts = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')
    fully_qualified_path_for_tar = os.path.join(local_directory, "%s-%s.tar" % (ts, required_notifier))
    print("Saving tar to %s" % fully_qualified_path_for_tar)

    cmd = "tar -cvf %s %s" % (fully_qualified_path_for_tar, " ".join(modified_files_from_git_status))
    s_run_process_and_get_output(cmd)

    print("\n\n----------------- TAR LOCATION -----------------\n\n")
    print(fully_qualified_path_for_tar)
    print("\n\n------------------------------------------------\n\n")
