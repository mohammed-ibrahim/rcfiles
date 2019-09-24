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
import uuid

# _________                         __                 __
# \_   ___ \  ____   ____   _______/  |______    _____/  |_  ______
# /    \  \/ /  _ \ /    \ /  ___/\   __\__  \  /    \   __\/  ___/
# \     \___(  <_> )   |  \\___ \  |  |  / __ \|   |  \  |  \___ \
#  \______  /\____/|___|  /____  > |__| (____  /___|  /__| /____  >
#         \/            \/     \/            \/     \/          \/
NEW_LINE = "\n"
IGNORE_OPEN_EDITOR = "--ignore-open-editor"
HR = "----------------------------------------------------------------------------------------------------------"

# ___________                            __  .__                   _____          __  .__               .___
# \_   _____/__  ___ ____   ____  __ ___/  |_|__| ____   ____     /     \   _____/  |_|  |__   ____   __| _/______
#  |    __)_\  \/  // __ \_/ ___\|  |  \   __\  |/  _ \ /    \   /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
#  |        \>    <\  ___/\  \___|  |  /|  | |  (  <_> )   |  \ /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \
# /_______  /__/\_ \\___  >\___  >____/ |__| |__|\____/|___|  / \____|__  /\___  >__| |___|  /\____/\____ /____  >
#         \/      \/    \/     \/                           \/          \/     \/          \/            \/    \/

update_branch_template = """

Submit New
rbt post -g -o

Update
rbt post -u

Smart Update
rbt post -u -o -r <review-id>

JENKINS :: origin/topic/%s/%s
REMOTE BRANCH :: %s

git branch --set-upstream-to=origin/master %s

git commit --amend
git commit --amend --no-edit

git pull
git rebase


a shead &&
git push origin :topic/%s/%s &&
git push origin HEAD:topic/%s/%s
"""
def update_branch(params, arg2, arg3, arg4, arg5, arg6, env_variables):

    current_branch = arg2
    if current_branch is None:
        current_branch = get_current_branch()

    current_user_details = s_run_process_and_get_output("whoami")
    current_user = current_user_details.split(NEW_LINE)[0]

    if "-j" in params:
        jenkin_cmd = "origin/topic/%s/%s" % (current_user, get_current_branch())
        print("Copied: %s" % jenkin_cmd)
        pyperclip.copy(jenkin_cmd)
        return

    required_url = "%s/commits/topic/%s/%s" % (get_repo_url(), current_user, current_branch)

    cmd = update_branch_template % (current_user, current_branch, required_url, current_branch, current_user, current_branch, current_user, current_branch)
    file_name = "%s.txt" % (get_qualifier_with_ctx())
    write_to_file(file_name, cmd)
    open_file_in_editor(file_name)

def head(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    head_diff = s_run_process_and_get_output('git show HEAD')
    file_name = "%s.%s.%s.diff" % (get_qualifier_with_ctx(), get_head_commit_id(), slugify(get_current_branch()))
    write_to_file(file_name, process_diff_file(head_diff))
    open_file_in_editor(file_name)

def shead(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    head_diff = s_run_process_and_get_output('git show HEAD')
    file_name = "%s.%s.%s.diff" % (get_qualifier_with_ctx(), get_head_commit_id(), slugify(get_current_branch()))
    write_to_file(file_name, head_diff)
    return file_name

def lhead(params, arg2, arg3, arg4, arg5, arg6, env_variables):
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

    file_name = "%s.diff" % get_qualifier_with_ctx()
    write_to_file(file_name, NEW_LINE.join(all_lines))
    # open_file_in_editor(file_name)
    open_file_in_editor_if_specified(params, file_name)

def git_copy(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    process_output = s_run_process_and_get_output('git status')
    lines = process_output.split(NEW_LINE)
    tabbed_lines = [line[1:] for line in lines if line.startswith("\t")]
    filtered_lines = [line for line in tabbed_lines if len(line.strip()) > 0]
    modified = "modified:   "
    if "-m" in params:
        filtered_lines = [line for line in filtered_lines if modified in line]
    filtered_lines = [line.replace(modified, "") for line in filtered_lines]
    pyperclip.copy(" ".join(filtered_lines))

def open_branch(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    current_branch = arg2
    if current_branch is None:
        current_branch = get_current_branch()

    current_user_details = s_run_process_and_get_output("whoami")
    current_user = current_user_details.split(NEW_LINE)[0]
    required_url = "%s/commits/topic/%s/%s" % (get_repo_url(), current_user, current_branch)
    open_url_in_browser(required_url)

merge_staging_template = """
git checkout dev/staging
git pull origin dev/staging
git merge origin/topic/{user}/{branch} --no-commit --no-ff
git commit
git push
"""
def merge_staging(params, arg2, arg3, arg4, arg5, arg6, env_variables):

    branch = arg2
    if branch is None:
        print("Need to send branch as parameter")
        err_exit()

    args = {
        'user': get_current_user(),
        'branch': branch
    }
    cmd = txt_substitute(merge_staging_template, args)
    file_name = "%s.txt" % (get_qualifier_with_ctx())
    write_to_file(file_name, cmd)
    open_file_in_editor(file_name)

merge_master_template = """
git checkout master
git pull origin master
git merge origin/topic/{user}/{branch} --no-commit --no-ff
git commit
git push
"""
def merge_master(params, arg2, arg3, arg4, arg5, arg6, env_variables):

    branch = arg2
    if branch is None:
        print("Need to send branch as parameter")
        err_exit()

    args = {
        'user': get_current_user(),
        'branch': branch
    }
    cmd = txt_substitute(merge_master_template, args)
    file_name = "%s.txt" % (get_qualifier_with_ctx())
    write_to_file(file_name, cmd)
    open_file_in_editor(file_name)

def save_url(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    url = arg2
    if url is None:
        print("Need to pass parameter for this command.")
        return

    file_name = get_qualifier_with_custom_ctx("url-save", "txt")
    req = requests.get(url)
    write_to_file(file_name, req.content)
    pyperclip.copy("vi %s" % file_name)
    open_file_in_editor_if_specified(params, file_name)

def save_curl(params, arg2, arg3, arg4, arg5, arg6, env_variables):
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
    open_file_in_editor_if_specified(params, file_name)

def save_diff(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    git_diff = s_run_process_and_get_output('git diff')
    file_name = "%s.diff" % get_qualifier_with_ctx()
    write_to_file(file_name, process_diff_file(git_diff))
    pyperclip.copy("vi %s" % file_name)
    open_file_in_editor(file_name)

def get_time_stamp(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    fully_qualified_path_for_backup = get_qualifier_with_ctx()
    pyperclip.copy(fully_qualified_path_for_backup)
    print("\n\n%s - copied to clipboard\n\n" % fully_qualified_path_for_backup)

def save_git_status(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    git_diff = s_run_process_and_get_output('git status')
    file_name = "%s.diff" % get_qualifier_with_ctx()
    write_to_file(file_name, git_diff)
    pyperclip.copy("vi %s" % file_name)
    open_file_in_editor(file_name)

def gen_uuid(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    ustr = str(uuid.uuid4())
    print("\n%s - copied to clipboard.\n" % ustr)
    pyperclip.copy(ustr)

def save_cmd_and_open(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    contents = read_stdin()
    file_name = "%s.cmd.out.txt" % get_qualifier_with_ctx()
    write_to_file(file_name, contents)
    open_file_in_editor(file_name)

def reduce_filenames(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    contents = read_stdin()
    lines = contents.split(NEW_LINE)
    filtered = [line.split("/") for line in lines if "/" in line]
    filtered = [parts[-1] for parts in filtered]

    if len(filtered) > 0:
        for file in filtered:
            print(file)
    else:
        print("No filenames in buffer")

def open_branch_ticket(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    if branch_to_use is None or branch_to_use.strip() == "":
        print("Couldn't determine branch")
        return

    local_directory = env_variables['TICKETS_DIR']
    repo_name = get_repo_url().split("/")[-1]
    ticket_name = "%s.%s.txt" % (slugify_c(repo_name), slugify_c(branch_to_use))
    file_identifier = os.path.join(local_directory, ticket_name)

    variables = {
        'repo_url': get_repo_url(),
        'user': get_current_user(),
        'branch': branch_to_use
    }

    if not os.path.isfile(file_identifier):
        # invoked first time:
        template_text = load_template_contents("ticket.txt")
        template_text = txt_substitute(template_text, variables)
        write_to_file(file_identifier, template_text)

    open_file_in_editor(file_identifier)

#  ____ ___   __  .__.__  .__  __              _____          __  .__               .___
# |    |   \_/  |_|__|  | |__|/  |_ ___.__.   /     \   _____/  |_|  |__   ____   __| _/______
# |    |   /\   __\  |  | |  \   __<   |  |  /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
# |    |  /  |  | |  |  |_|  ||  |  \___  | /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \
# |______/   |__| |__|____/__||__|  / ____| \____|__  /\___  >__| |___|  /\____/\____ /____  >
#                                   \/              \/     \/          \/            \/    \/
# --utility

# def get_temp_note_file_name():
#     return os.path.join(os.environ.get("HOME"), "TempNote.txt")
#
# def save_contents_to_base_trackpad(contents, open_in_editor):
#     temp_note_file = get_temp_note_file_name()
#     write_to_file(temp_note_file, contents)
#
#     if open_in_editor:
#         open_file_in_editor(temp_note_file)

def txt_substitute(input, replacement_vars):

    text = input
    for key in replacement_vars:
        rkey = "{%s}" % key
        rval = replacement_vars[key]

        text = text.replace(rkey, rval)

    return text

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

def get_repo_base_path():
    return os.path.dirname(os.path.abspath(__file__))

def load_template_contents(template_name):
    template_dir = os.path.join(get_repo_base_path(), "templates", template_name)
    print("Loading file: %s" % template_dir)
    return read_file_contents(template_dir)


NEXT_FILE = """



----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------
%s


"""

def process_diff_file(diff_text):
    lines = diff_text.split(NEW_LINE)
    buffer = []
    file_paths = []
    file_names = []

    for line in lines:
        if line.startswith("diff --git"):
            file_path = line.split(" ")[-1][2:]
            file_paths.append(file_path)

            file_name = line.split("/")[-1]
            file_names.append(file_name)

            buffer.append(NEXT_FILE % (file_name))

        buffer.append(line)

    p1 = NEW_LINE.join(file_paths)
    p2 = NEW_LINE.join(file_names)
    fn = "\n\n\n%s\n%s\n\n%s\n\n%s\n\n" % (p1, HR, p2, HR)
    buffer = [fn] + buffer

    return NEW_LINE.join(buffer)

def read_stdin():
    try:
        return sys.stdin.read()
    except Exception as e:
        print e.args
        return None

def get_current_user():
    current_user_details = s_run_process_and_get_output("whoami")
    return current_user_details.split(NEW_LINE)[0]

def open_url_in_browser(url):
    webbrowser.open(url, new=0, autoraise=True)

def open_file_in_editor_if_specified(params, file_name):
    if "--atom" in params:
        open_file_in_editor(file_name)

def open_file_in_editor(file_name):
    s_run_process_and_get_output("/usr/local/bin/atom %s" % file_name)

def get_qualifier_with_ctx():
    # ctx = get_param(2)
    # if ctx is None:
    #     ctx = get_cwd_name()
    # else:
    #     ctx = slugify(ctx)

    ctx = get_cwd_name()
    local_directory = env_variables['LOCAL_BACKUP_DIR']
    return os.path.join(local_directory, "%s-%s" % (ctx, get_ts()))

def get_qualifier_with_custom_ctx(ctx, extension):
    ctx = slugify(ctx)
    local_directory = env_variables['LOCAL_BACKUP_DIR']
    return os.path.join(local_directory, "%s-%s.%s" % (ctx, get_ts(), extension))

def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)

def get_head_commit_id():
    return s_run_process_and_get_output('git rev-parse HEAD').replace(NEW_LINE, "").strip()

def get_ts():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')

def slugify(text):
    # output = re.sub(r'\W+', '-', text)
    # return output.lower()
    return slugify_c(text).lower()

def slugify_c(text):
    output = re.sub(r'\W+', '-', text)
    return output

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

    env_variables = {
        'LOCAL_BACKUP_DIR': pull_env_var('LOCAL_BACKUP_DIR'),
        'TICKETS_DIR': pull_env_var('TICKETS_DIR')
    }

    primary_operations = [
        get_cmd("ub",       "Update Branch Commands.",              "-j", update_branch),
        get_cmd("head",     "Save head commit & Open in editor.",   "non", head),
        get_cmd("shead",    "Save head commit patch to backup.",    "non", shead),
        get_cmd("lhead",    "List file in head commit.",            "non", lhead),
        get_cmd("ob",       "Open Branch",                          "non", open_branch),
        get_cmd("ms",       "Merge into staging",                   "non", merge_staging),
        get_cmd("mm",       "Merge into master",                    "non", merge_master),
        get_cmd("url",      "Save url output to file",              "non", save_url),
        get_cmd("curl",     "Save curl output to file",             "non", save_curl),
        get_cmd("diff",     "Save git diff",                        "non", save_diff),
        get_cmd("ts",       "Get backup time stamp",                "non", get_time_stamp),
        get_cmd("gs",       "Save git status to file",              "non", save_git_status),
        get_cmd("uuid",     "Generate new uuid",                    "non", gen_uuid),
        get_cmd("sc",       "Save cmd output to file & open",       "non", save_cmd_and_open),
        get_cmd("gc",       "Copy and concat git status files",     "-m" , git_copy),
        get_cmd("red",      "Reduce to filenames",                  "non" , reduce_filenames),
        get_cmd("o",        "Open branch specifiec file",           "branch_name" , open_branch_ticket)
    ]

    primary_operation_codes = [x['code'] for x in primary_operations]
    mode = get_param(1)
    if mode is None or mode not in primary_operation_codes:
        display_primary_operations(primary_operations)
        err_exit()

    index = primary_operation_codes.index(mode)
    arg = primary_operations[index]
    fn = arg['fnc']
    fn(get_params(), get_param(2), get_param(3), None, None, None, env_variables)
