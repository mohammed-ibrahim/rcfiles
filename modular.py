import subprocess
import json
import os
import sys
import datetime
import time
import pyperclip
import re
import requests
import webbrowser

# _________                         __                 __
# \_   ___ \  ____   ____   _______/  |______    _____/  |_  ______
# /    \  \/ /  _ \ /    \ /  ___/\   __\__  \  /    \   __\/  ___/
# \     \___(  <_> )   |  \\___ \  |  |  / __ \|   |  \  |  \___ \
#  \______  /\____/|___|  /____  > |__| (____  /___|  /__| /____  >
#         \/            \/     \/            \/     \/          \/
NEW_LINE = "\n"

# ___________                            __  .__                   _____          __  .__               .___
# \_   _____/__  ___ ____   ____  __ ___/  |_|__| ____   ____     /     \   _____/  |_|  |__   ____   __| _/______
#  |    __)_\  \/  // __ \_/ ___\|  |  \   __\  |/  _ \ /    \   /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
#  |        \>    <\  ___/\  \___|  |  /|  | |  (  <_> )   |  \ /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \
# /_______  /__/\_ \\___  >\___  >____/ |__| |__|\____/|___|  / \____|__  /\___  >__| |___|  /\____/\____ /____  >
#         \/      \/    \/     \/                           \/          \/     \/          \/            \/    \/


def update_branch(params, arg2, arg3, arg4, arg5, arg6):
    update_branch_template = """

    JENKINS :: origin/topic/%s/%s
    REMOTE BRANCH :: %s

    git branch --set-upstream-to=origin/master %s

    git commit --amend
    git commit --amend --no-edit

    git pull
    git rebase


    a sci &&
    git push origin :topic/%s/%s &&
    git push origin HEAD:topic/%s/%s
    """
    current_branch = arg1
    if current_branch is None:
        current_branch = get_current_branch()

    current_user_details = s_run_process_and_get_output("whoami")
    current_user = current_user_details.split(NEW_LINE)[0]
    required_url = "%s/commits/topic/%s/%s" % (get_repo_url(), current_user, current_branch)

    if cmd is not None:
        if cmd == open_branch_link:
            webbrowser.open(required_url, new=0, autoraise=True)
            return

    cmd = update_branch_template % (current_user, current_branch, required_url, current_branch, current_user, current_branch, current_user, current_branch)
    print(cmd)

def head(params, arg2, arg3, arg4, arg5, arg6):
    head_diff = s_run_process_and_get_output('git show HEAD')
    file_name = "%s.diff" % get_qualifier_with_ctx()
    write_to_file(file_name, head_diff)
    pyperclip.copy("vi %s" % file_name)

def lhead(params, arg2, arg3, arg4, arg5, arg6):
    lhead_diff = s_run_process_and_get_output('git diff-tree --no-commit-id --name-only -r HEAD')
    all_lines = [line for line in lhead_diff.split("\n") if len(line) > 0]
    gc_param = arg2

    if gc_param == "-gc":
        print("\n\n%s\n\n" % (" ".join(all_lines)))
    else:
        print("\n\n")
        for line in all_lines:
            print(line)
        print("\n\n")

def git_copy(params, arg2, arg3, arg4, arg5, arg6):
    process_output = s_run_process_and_get_output('git status -s')
    files = [x[3:] for x in process_output.split("\n") if len(x.strip()) > 0]
    param = arg2
    text = None
    if param is None:
        text = " ".join(files)
    else:
        index = int(param)
        if index >= len(files) or index < 0:
            print("Invalid index")
            for i in range(len(files)):
                print("%s :: %s" % (i, files[i]))
        text = files[index]

    pyperclip.copy(text)

def open_branch(params, arg2, arg3, arg4, arg5, arg6):
    current_branch = arg2
    if current_branch is None:
        current_branch = get_current_branch()

    current_user_details = s_run_process_and_get_output("whoami")
    current_user = current_user_details.split(NEW_LINE)[0]
    required_url = "%s/commits/topic/%s/%s" % (get_repo_url(), current_user, current_branch)
    webbrowser.open(required_url, new=0, autoraise=True)

def merge_staging(params, arg2, arg3, arg4, arg5, arg6):
    merge_staging_template = """
    git checkout dev/staging
    git pull origin dev/staging
    git merge origin/topic/%s/%s --no-commit --no-ff
    git commit
    git push
    """
    branch = arg2
    if branch is None:
        print("Need to send branch as parameter")
        err_exit()

    print(merge_staging_template % (get_current_user(), branch))

def merge_master(params, arg2, arg3, arg4, arg5, arg6):
    merge_master_template = """
    git checkout master
    git pull origin master
    git merge origin/topic/%s/%s --no-commit --no-ff
    git commit
    git push
    """
    branch = arg2
    if branch is None:
        print("Need to send branch as parameter")
        err_exit()

    print(merge_master_template % (get_current_user(), branch))

def save_url(params, arg2, arg3, arg4, arg5, arg6):
    url = arg2
    if url is None:
        print("usage: a %s <url>" % (URL['code']))
        return

    file_name = get_qualifier_with_custom_ctx("url-save", "txt")
    req = requests.get(url)
    write_to_file(file_name, req.content)
    pyperclip.copy("vi %s" % file_name)

def save_curl(params, arg2, arg3, arg4, arg5, arg6):
    url = None
    headers = {}
    extension = "txt"

    for i in range(len(params)):
        part = params[i]
        if part.lower() == 'curl':
            continue

        if part == "-H":
            next_part = params[i+1]
            parts = next_part.split(": ")
            headers[parts[0]] = parts[1]

        if part.lower() == "-e":
            extension = params[i+1]

        if part.startswith("http"):
            url = part

    if url is None:
        print("Invalid command")
        return

    file_name = get_qualifier_with_custom_ctx("curl-save", extension)
    req = requests.get(url, headers = headers)
    write_to_file(file_name, req.content)
    pyperclip.copy("vi %s" % file_name)

def save_diff(params, arg2, arg3, arg4, arg5, arg6):
    git_diff = s_run_process_and_get_output('git diff')
    file_name = "%s.diff" % get_qualifier_with_ctx()
    write_to_file(file_name, git_diff)
    pyperclip.copy("vi %s" % file_name)

def get_time_stamp(params, arg2, arg3, arg4, arg5, arg6):
    fully_qualified_path_for_backup = get_qualifier_with_ctx()
    pyperclip.copy(fully_qualified_path_for_backup)
    print("\n\n%s - copied to clipboard\n\n" % fully_qualified_path_for_backup)

#  ____ ___   __  .__.__  .__  __              _____          __  .__               .___
# |    |   \_/  |_|__|  | |__|/  |_ ___.__.   /     \   _____/  |_|  |__   ____   __| _/______
# |    |   /\   __\  |  | |  \   __<   |  |  /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
# |    |  /  |  | |  |  |_|  ||  |  \___  | /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \
# |______/   |__| |__|____/__||__|  / ____| \____|__  /\___  >__| |___|  /\____/\____ /____  >
#                                   \/              \/     \/          \/            \/    \/
# --utility

def get_qualifier_with_ctx():
    ctx = get_param(2)
    if ctx is None:
        ctx = get_cwd_name()
    else:
        ctx = slugify(ctx)

    local_directory = pull_env_var('LOCAL_BACKUP_DIR')
    return os.path.join(local_directory, "%s-%s" % (ctx, get_ts()))

def get_qualifier_with_custom_ctx(ctx, extension):
    ctx = slugify(ctx)
    local_directory = pull_env_var('LOCAL_BACKUP_DIR')
    return os.path.join(local_directory, "%s-%s.%s" % (ctx, get_ts(), extension))

def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)

def get_ts():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')

def slugify(text):
    output = re.sub(r'\W+', '-', text)
    return output.lower()

def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        err_exit()

    return env_value

def get_cwd_name():
    cwd = os.getcwd()
    path_parts = cwd.split("/")
    cwd_name = path_parts.pop().strip()
    return cwd_name

def get_repo_url():
    process_output = s_run_process_and_get_output('git config remote.origin.url')
    return 'https://' + process_output.split("@")[1].replace(":", "/")[:-5]

def run_process_and_get_output(command_list, exit_on_failure=False):
    print("Executing ::: %s" % " ".join(command_list))
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        err_exit()

    return out

def err_exit():
    sys.exit(1)

def s_run_process_and_get_output(s_cmd, exit_on_failure=False):
    return run_process_and_get_output(s_cmd.split(" "), exit_on_failure)

def get_non_cmd_params():
    non_cmd_list = []
    for i in range(2, len(sys.argv)):
        cmd = sys.argv[i]
        if not cmd.startswith("-"):
            non_cmd_list.append(cmd)

    return non_cmd_list

def get_current_branch():
    branch_details = s_run_process_and_get_output("git branch")
    current_branch = [x for x in branch_details.split(NEW_LINE) if "*" in x][0]
    return current_branch[2:]

def get_cmd(code, desc, options, fnc):
    return {
        "code": code,
        "desc": desc,
        "options": options,
        "fnc": fnc
    }

def display_primary_operations(primary_operations):
    primary_operation_codes = [x['code'] for x in primary_operations]
    print("usage: :: a [%s]" % (",".join(primary_operation_codes)))
    for cmd in primary_operations:
        print("\t\t%s \t\t[%s]" % (cmd['code'], cmd['desc']))

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


# __________                                             ___________ __
# \______   \_______  ____   ________________    _____   \_   _____//  |_  ___________ ___.__.
#  |     ___/\_  __ \/  _ \ / ___\_  __ \__  \  /     \   |    __)_\   __\/    \_  __ <   |  |
#  |    |     |  | \(  <_> ) /_/  >  | \// __ \|  Y Y  \  |        \|  | |   |  \  | \/\___  |
#  |____|     |__|   \____/\___  /|__|  (____  /__|_|  / /_______  /|__| |___|  /__|   / ____|
#                         /_____/            \/      \/          \/           \/       \/
# --main

if __name__ == "__main__":

    primary_operations = [
        get_cmd("ub", "Update Branch Commands.", "non", update_branch),
        get_cmd("head", "Save head commit patch to backup.", "non", head),
        get_cmd("lhead", "List file in head commit.", "non", lhead),
        get_cmd("gp", "Git status copy", "-ob", git_copy),
        get_cmd("ob", "Open Branch", "non", open_branch),
        get_cmd("ms", "Merge into staging", "non", merge_staging),
        get_cmd("mm", "Merge into master", "non", merge_master),
        get_cmd("url", "Merge into master", "non", save_url),
        get_cmd("curl", "Merge into master", "non", save_curl),
        get_cmd("diff", "Save git diff", "non", save_diff),
        get_cmd("ts", "Get backup time stamp", "non", get_time_stamp)
    ]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = get_param(1)
    if mode is None or mode not in primary_operation_codes:
        display_primary_operations(primary_operations)
        err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']
    fn(get_params(), get_param(2), get_param(3), None, None, None)
