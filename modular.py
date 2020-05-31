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
import urllib

# _________                         __                 __
# \_   ___ \  ____   ____   _______/  |______    _____/  |_  ______
# /    \  \/ /  _ \ /    \ /  ___/\   __\__  \  /    \   __\/  ___/
# \     \___(  <_> )   |  \\___ \  |  |  / __ \|   |  \  |  \___ \
#  \______  /\____/|___|  /____  > |__| (____  /___|  /__| /____  >
#         \/            \/     \/            \/     \/          \/

class Timer():

    _start_time = None
    def __init__(self):
        self._start_time = datetime.datetime.now()

    def end(self):
        end_time = datetime.datetime.now()
        delta = end_time - self._start_time
        return str(delta)


NEW_LINE = "\n"
IGNORE_OPEN_EDITOR = "--ignore-open-editor"
EDITOR_ATOM = "atom"
EDITOR_VIM = "vim"
HR = "----------------------------------------------------------------------------------------------------------"

# ___________                            __  .__                   _____          __  .__               .___
# \_   _____/__  ___ ____   ____  __ ___/  |_|__| ____   ____     /     \   _____/  |_|  |__   ____   __| _/______
#  |    __)_\  \/  // __ \_/ ___\|  |  \   __\  |/  _ \ /    \   /  \ /  \_/ __ \   __\  |  \ /  _ \ / __ |/  ___/
#  |        \>    <\  ___/\  \___|  |  /|  | |  (  <_> )   |  \ /    Y    \  ___/|  | |   Y  (  <_> ) /_/ |\___ \
# /_______  /__/\_ \\___  >\___  >____/ |__| |__|\____/|___|  / \____|__  /\___  >__| |___|  /\____/\____ /____  >
#         \/      \/    \/     \/                           \/          \/     \/          \/            \/    \/



update_branch_template = """
----------------------------------------------------------------------------------------
RB new                  ::   rbt post -g -o
RB Update               ::   rbt post -r <review-id> <latest-commit-id>

Jenkins                 ::   origin/topic/{user}/{branch}
Remote Branch           ::   {repo_url}/commits/topic/{user}/{branch}

Upstream                ::   git branch --set-upstream-to=origin/master {branch}

Amend                   ::   git commit --amend
Amend no-edid           ::   git commit --amend --no-edit

Update commit           ::   git pull && git rebase

Push to remote branch   ::   a shead &&
                             git push origin :topic/{user}/{branch} &&
                             git push origin HEAD:topic/{user}/{branch}

Merge Staging           ::   git checkout dev/staging &&
                             git pull origin dev/staging
                             git merge origin/topic/{user}/{branch} --no-commit --no-ff
                             git commit
                             git push

Merge Master            ::   git checkout master &&
                             git pull origin master
                             git merge origin/topic/{user}/{branch} --no-commit --no-ff
                             git commit
                             git push
----------------------------------------------------------------------------------------
"""
def update_branch(params, arg2, arg3, arg4, arg5, arg6, env_variables):

    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    if branch_to_use is None or branch_to_use.strip() == "":
        print("Couldn't determine branch")
        return

    local_directory = env_variables['TICKETS_DIR']
    ticket_name = "%s.txt" % (slugify_c(branch_to_use))
    file_identifier = os.path.join(local_directory, ticket_name)

    variables = {
        'repo_url': get_repo_url(),
        'user': get_current_user(),
        'branch': branch_to_use
    }

    cmd = txt_substitute(update_branch_template, variables)
    # cmd = update_branch_template % (current_user, current_branch, required_url, current_branch, current_user, current_branch, current_user, current_branch)
    # file_name = "%s.txt" % (get_qualifier_with_ctx())
    # write_to_file(file_name, cmd)
    # open_file_in_editor(file_name)

    print(cmd)

def copy_full_branch(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    jenkin_cmd = "origin/topic/%s/%s" % (get_current_user(), branch_to_use)
    pyperclip.copy(jenkin_cmd)
    print("Copied: %s" % jenkin_cmd)

def head(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    head_diff = s_run_process_and_get_output('git show HEAD')
    file_name = "%s.%s.%s.diff" % (get_qualifier_with_ctx(env_variables), get_head_commit_id(), slugify(get_current_branch()))
    write_to_file(file_name, process_diff_file(head_diff))
    pyperclip.copy("vi %s" % file_name)
    # open_file_in_editor(file_name)

def shead(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    head_diff = s_run_process_and_get_output('git show HEAD')
    file_name = "%s.%s.%s.diff" % (get_qualifier_with_ctx(env_variables), get_head_commit_id(), slugify(get_current_branch()))
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

    file_name = "%s.diff" % get_qualifier_with_ctx(env_variables)
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

def save_url(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    url = arg2
    if url is None:
        print("Need to pass parameter for this command.")
        return

    file_name = get_qualifier_with_custom_ctx("url-save", "txt", env_variables)
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

    file_name = get_qualifier_with_custom_ctx("curl-save", extension, env_variables)
    req = requests.get(url, headers = headers)
    write_to_file(file_name, req.content)
    pyperclip.copy("vi %s" % file_name)
    open_file_in_editor_if_specified(params, file_name)

def save_diff(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    git_diff = s_run_process_and_get_output('git diff')
    file_name = "%s.diff" % get_qualifier_with_ctx(env_variables)
    write_to_file(file_name, process_diff_file(git_diff))
    pyperclip.copy("vi %s" % file_name)
    # open_file_in_editor(file_name, EDITOR_VIM)

def get_time_stamp(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    fully_qualified_path_for_backup = get_qualifier_with_ctx(env_variables)
    pyperclip.copy(fully_qualified_path_for_backup)
    print("\n\n%s - copied to clipboard\n\n" % fully_qualified_path_for_backup)

def save_git_status(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    git_diff = s_run_process_and_get_output('git status')
    file_name = "%s.diff" % get_qualifier_with_ctx(env_variables)
    write_to_file(file_name, git_diff)
    pyperclip.copy("vi %s" % file_name)
    open_file_in_editor(file_name, EDITOR_ATOM)

def gen_uuid(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    ustr = str(uuid.uuid4())
    print("\n%s - copied to clipboard.\n" % ustr)
    pyperclip.copy(ustr)

def save_cmd_and_open(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    contents = read_stdin()
    file_name = "%s.cmd.out.txt" % get_qualifier_with_ctx(env_variables)
    write_to_file(file_name, contents)
    open_file_in_editor(file_name, EDITOR_ATOM)

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
    ticket_name = "%s.txt" % (slugify_c(branch_to_use))
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

    open_file_in_editor(file_identifier, EDITOR_ATOM)

def slugify_cmd_line(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    if len(params) < 1:
        print("need params to be slugified")
        err_exit()

    text = " ".join(params)
    text = slugify(text)
    pyperclip.copy(text)
    print(text)

CTC_TEMPLATE = """

-------------------------------------------------------------
Diff Status      ::  {diff_status}
Title            ::  {title}
Local Commit     ::  {local_commit_id}
Remote Commit    ::  {remote_commit_id}
-------------------------------------------------------------

"""
def compare_top_commit(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    local_commit_id = get_head_commit_for_branch(branch_to_use)
    remote_commit_details = get_remote_branch_top_commit_details(branch_to_use, env_variables)
    if remote_commit_details is None:
        print("There was an error fetching remote branch details")
        err_exit()

    remote_commit_id = remote_commit_details['id']
    title = remote_commit_details['title']
    diff_status = "!!COMMITS DIFFER!!"

    if local_commit_id == remote_commit_id:
        diff_status = "Commits are Same"

    variables = {
        'local_commit_id': local_commit_id,
        'remote_commit_id': remote_commit_id,
        'title': title,
        'diff_status': diff_status
    }

    text = txt_substitute(CTC_TEMPLATE, variables)
    print(text)


def enlist_branches(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is not None:
        top_commit_details = get_remote_branch_top_commit_details(branch_to_use, env_variables)
        if top_commit_details is not None:
            print("\n\n%s - %s\n\n" % (branch_to_use, top_commit_details['title']))
        else:
            print("Failed to fetch branch details")

        sys.exit(0)

    text = s_run_process_and_get_output("git branch")
    lines = text.split("\n")
    lines = [a[2:] for a in lines if len(a.strip()) > 0]
    branches = [a for a in lines if a not in ['master', 'dev/staging']]

    buffer = []
    index = 1
    for branch in branches:
        top_commit_details = get_remote_branch_top_commit_details(branch, env_variables)
        if top_commit_details is not None:
            buffer.append("%s - %s" % (branch.ljust(30), top_commit_details['title']))

    print("\n\n----------------------------------------------------------------")
    print("\n".join(buffer))
    print("----------------------------------------------------------------\n\n")

def open_jira_ticket(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    jira_domain = env_variables['JIRA_DOMAIN']
    jira_url = "%s/jira/browse/%s" % (jira_domain, branch_to_use)
    open_url_in_browser(jira_url)

def open_repository(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    repo_url = get_repo_url()
    open_url_in_browser(repo_url)

def load_all_mocks(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    url = "http://localhost:1080/mockserver/retrieve?type=ACTIVE_EXPECTATIONS"
    req = requests.put(url)
    status_code = req.status_code

    if status_code == 200:
        data = json.loads(req.content)
        file_name = "%s.mock.expectations.txt" % get_qualifier_with_ctx(env_variables)
        write_to_file(file_name, json.dumps(data, indent=4))
        open_file_in_editor(file_name, EDITOR_ATOM)
    else:
        print("There was problem communicating to : %s ::: %s" % (url, req.content))

def copy_amend(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    is_safe_to_amend()
    pyperclip.copy("git commit --amend")

def copy_amend_no_edit(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    is_safe_to_amend()
    pyperclip.copy("git commit --amend --no-edit")


def safe_push_remote_branch(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    """
    1. Ensure that it is not staging or master branch
    2. Ensure there are no diffs
    3. Ensure no staged files for commit
    4. Check whether remote branch exists
    """

    timer = Timer()
    branch_to_use = get_current_branch()

    if branch_to_use in ["master", "dev/staging", "staging"]:
        print("Cannot auto push to this branch: " + branch_to_use)
        err_exit()

    git_diff = s_run_process_and_get_output('git diff')
    if len(git_diff.strip()) > 0:
        print("Code diff is present plz check before pushing")
        err_exit()

    stage_files = s_run_process_and_get_output('git diff --name-only --cached')
    if len(stage_files.strip()) > 0:
        print("There are staged files present")
        err_exit()

    remote_branch_details = get_remote_branch_top_commit_details(branch_to_use, env_variables)
    output = "None"

    delete_template = "git push origin :topic/{user}/{branch}"
    delete_command = txt_substitute(delete_template, {'user': get_current_user(), 'branch': branch_to_use})

    push_template = "git push origin HEAD:topic/{user}/{branch}"
    push_command = txt_substitute(push_template, {'user': get_current_user(), 'branch': branch_to_use})

    if remote_branch_details is None:
        # Only Push
        output = s_run_process_and_get_output(push_command)
    else:
        # Delete and push
        output1 = s_run_process_and_get_output(delete_command)
        output2 = s_run_process_and_get_output(push_command)
        output = output1 + "\n\n\n" + output2

    print("Command output: %s \n\n\nTime taken: %s" % (output, timer.end()))


def merge_to_staging(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    source_branch_name = arg2
    target_branch_name = 'dev/staging'
    resolve_pre_merge(source_branch_name, target_branch_name, env_variables)

def merge_to_master(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    source_branch_name = arg2
    target_branch_name = 'master'
    resolve_pre_merge(source_branch_name, target_branch_name, env_variables)

def run_rbt_utility(params, arg2, arg3, arg4, arg5, arg6, env_variables):
    branch_to_use = arg2
    if branch_to_use is None:
        branch_to_use = get_current_branch()

    if branch_to_use is None or branch_to_use.strip() == "":
        print("Couldn't determine branch")
        return

    command_output = s_run_process_and_get_output("git log -3 %s" % branch_to_use, exit_on_failure=True)
    prefix = "rbt post -g -o\nrbt post -r <review-id> <latest-commit-id>\n\n\n"
    temp_file_name = get_qualifier_with_custom_ctx("temp", "txt", env_variables)
    write_to_file(temp_file_name, prefix + command_output)
    open_file_in_editor(temp_file_name, EDITOR_ATOM)

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

def is_safe_to_amend():
    branch_to_use = get_current_branch()
    if branch_to_use in ["master", "dev/staging", "staging"]:
        print("cannot amend to this branch: " + branch_to_use)
        err_exit()

    git_diff = s_run_process_and_get_output('git diff')
    if len(git_diff.strip()) > 0:
        print("cannot amend when there is diff")
        err_exit()

    stage_files = s_run_process_and_get_output('git diff --name-only --cached')
    if len(stage_files.strip()) < 1:
        print("Nothing to amend")
        err_exit()

    return True

def resolve_pre_merge(source_branch_name, target_branch_name, env_variables):
    timer = Timer()

    print("Merging %s into %s" % (source_branch_name, target_branch_name))

    if source_branch_name == target_branch_name:
        print("Cannot merge: %s into: %s" % (source_branch_name, target_branch_name))
        err_exit()

    if source_branch_name is None:
        print("Branch name is necessary to merge")
        err_exit()

    if source_branch_name in ["master", "dev/staging", "staging"]:
        print("This cannot be source branch: " + source_branch_name)
        err_exit()

    source_branch_local_commmit_id = get_head_commit_for_branch(source_branch_name)
    source_branch_remote_commit_details = get_remote_branch_top_commit_details(source_branch_name, env_variables)

    if source_branch_remote_commit_details is None:
        print("Destination branch doesnt exists: " + source_branch_name)
        err_exit()

    source_branch_remote_commit_id = source_branch_remote_commit_details['id']

    if source_branch_local_commmit_id != source_branch_remote_commit_id:
        print("Local commit: %s Remote commit: %s differ for branch: %s" % (source_branch_local_commmit_id, source_branch_remote_commit_id, source_branch_name))
        err_exit()

    print("Commit id matches remote and local for branch: %s commit: %s" % (source_branch_name, source_branch_remote_commit_id))

    s_run_process_and_get_output('git checkout ' + target_branch_name)
    s_run_process_and_get_output('git pull')
    s_run_process_and_get_output('git pull origin ' + target_branch_name)
    s_run_process_and_get_output('git pull')

    target_branch_local_commit_id = get_head_commit_for_branch(target_branch_name)
    target_branch_remote_commit_details = get_remote_branch_top_commit_details(target_branch_name, env_variables)
    if target_branch_remote_commit_details is None:
        print("There was an error fetching remote branch details: branch: %s" % target_branch_name)
        err_exit()

    target_branch_remote_commit_id = target_branch_remote_commit_details['id']
    #title = target_branch_remote_commit_details['title']

    if target_branch_local_commit_id != target_branch_remote_commit_id:
        print("Local commit: %s Remote commit: %s differ for branch: %s" % (target_branch_local_commit_id, target_branch_remote_commit_id, target_branch_name))
        err_exit()

    print("Commit id matches remote and local for branch: %s commit: %s" % (target_branch_name, target_branch_remote_commit_id))

    merge_command_template = "git merge origin/topic/{user}/{branch} --no-ff"
    merge_command = txt_substitute(merge_command_template, {'user': get_current_user(), 'branch': source_branch_name})
    pyperclip.copy(merge_command)
    print("Copyed to the clipboard: %s time taken: %s" % (merge_command, timer.end()))

def ensure_commit_hash_has_value(commit_hash_text, key):
    lines = commit_hash_text.split("\n")
    filtered_lines = [a.strip() for a in lines if key in a]

    if len(filtered_lines) != 1:
        print("just 1 entry for key not found in text: %s" % commit_hash_text)
        err_exit()

    required_line = filtered_lines[0].strip()
    filtered_text = required_line.replace(key, "")
    if len(filtered_text) > 0:
        return

    print("Insufficent entry for : %s" % key)
    err_exit()


def find_ticket(base_dir, ticket_name):
    sub_directores = []

    for file in os.listdir(base_dir):
        current_base_dir_items = os.path.join(base_dir, file)
        if os.path.isdir(current_base_dir_items):
            sub_directores.append(current_base_dir_items)

    for sub_dir in sub_directores:

        for file_in_subdir in os.listdir(sub_dir):

            current_subdirectory_item = os.path.join(sub_dir, file_in_subdir)
            if os.path.isfile(current_subdirectory_item) and file_in_subdir == ticket_name:
                return current_subdirectory_item

    return None

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
        print(e.args)
        return None

def get_current_user():
    current_user_details = s_run_process_and_get_output("whoami")
    return current_user_details.split(NEW_LINE)[0]

def open_url_in_browser(url):
    webbrowser.open(url, new=0, autoraise=True)

def open_file_in_editor_if_specified(params, file_name):
    if "--atom" in params:
        open_file_in_editor(file_name, EDITOR_ATOM)

# def open_file_in_editor(file_name):
#     open_file_in_editor(file_name, EDITOR_ATOM)

def open_file_in_editor(file_name, editor):

    if editor == EDITOR_ATOM:
        s_run_process_and_get_output("/usr/local/bin/atom %s" % file_name)
    else:
        s_run_process_and_get_output("vi %s" % file_name)


def get_qualifier_with_ctx(env_variables):
    # ctx = get_param(2)
    # if ctx is None:
    #     ctx = get_cwd_name()
    # else:
    #     ctx = slugify(ctx)

    ctx = get_cwd_name()
    local_directory = env_variables['LOCAL_BACKUP_DIR']
    return os.path.join(local_directory, "%s-%s" % (ctx, get_ts()))

def get_qualifier_with_custom_ctx(ctx, extension, env_variables):
    ctx = slugify(ctx)
    local_directory = env_variables['LOCAL_BACKUP_DIR']
    return os.path.join(local_directory, "%s-%s.%s" % (ctx, get_ts(), extension))

def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:

        if type(content) == str:
            file_pointer.write(content)
        else:
            file_pointer.write(content.decode("utf-8"))

    print("File write complete: " + file_name)

def get_head_commit_id():
    return s_run_process_and_get_output('git rev-parse HEAD').replace(NEW_LINE, "").strip()

def get_head_commit_for_branch(branch_name):
    process_output = s_run_process_and_get_output('git log -1 %s' % branch_name)
    first_line = process_output.split("\n")[0]
    parts = first_line.split(" ")
    if len(parts) < 2:
        print("Failed to parse the data: %s" % process_output)
        err_exit()

    commit_id = parts[1]
    return commit_id

def get_remote_branch_top_commit_details(branch_name, env_variables):

    remote_branch = None
    if branch_name in ['master', 'staging']:
        remote_branch = branch_name
    elif branch_name == 'dev/staging':
        remote_branch = 'dev/staging'
    else:
        remote_branch = "topic/%s/%s" % (get_current_user(), branch_name)

    gitlab_domain = env_variables['GITLAB_DOMAIN']
    gitlab_api_key = env_variables['GITLAB_API_KEY']
    header = {
        'PRIVATE-TOKEN': gitlab_api_key
    }

    gitlab_api = "https://%s/api/v4/projects/%s/repository/commits/%s" % (gitlab_domain, get_gitlab_api_project_key(), url_encode(remote_branch))
    req = requests.get(gitlab_api, headers = header)
    status_code = req.status_code

    if status_code == 200:
        data = json.loads(req.content)
        return data
    else:
        print("There was problem communicating to : %s ::: %s" % (gitlab_api, req.content))
        return None

def get_gitlab_api_project_key():
    process_output = s_run_process_and_get_output('git config remote.origin.url')
    process_output = process_output.split(":")[1][:-5]
    return url_encode(process_output)

def url_encode(s):
    return urllib.parse.quote_plus(s)

def get_ts():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')

def slugify(text):
    # output = re.sub(r'\W+', '-', text)
    # return output.lower()
    return slugify_c(text).lower()

def slugify_c(text):
    output = re.sub(r'\W+', '-', text)
    return output.strip("-")

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

    return out.decode("utf-8")

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

def parse_branch_name_from_current_git_branch(branch_name):
    branch_name = branch_name[2:] # remove '* '
    # num_dashes = branch_name.count("-")
    #
    # if num_dashes > 1:
    #     index_of_second_count = branch_name.replace("-", "=", 1).index("-")
    #     branch_name = branch_name[0:index_of_second_count]

    return branch_name

def get_current_branch():
    branch_details = s_run_process_and_get_output("git branch")
    marked_branches = [x for x in branch_details.split(NEW_LINE) if "*" in x]
    if len(marked_branches) < 1:
        print("git branch didnt return any marked branches.")
        err_exit()
    current_branch = marked_branches[0]
    return parse_branch_name_from_current_git_branch(current_branch)

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
        'TICKETS_DIR': pull_env_var('TICKETS_DIR'),
        'GITLAB_DOMAIN': pull_env_var('GITLAB_DOMAIN'),
        'GITLAB_API_KEY':  pull_env_var('GITLAB_API_KEY'),
        'JIRA_DOMAIN': pull_env_var('JIRA_DOMAIN')
    }

    primary_operations = [
        get_cmd("ub",       "Update Branch Commands.",              "non", update_branch),
        get_cmd("j",        "Copy full branch for Jenkins Command",                  "non", copy_full_branch),
        get_cmd("head",     "Save head commit & Open in editor.",   "non", head),
        get_cmd("shead",    "Save head commit patch to backup.",    "non", shead),
        get_cmd("lhead",    "List file in head commit.",            "non", lhead),
        get_cmd("ob",       "Open Branch",                          "non", open_branch),
        get_cmd("url",      "Save url output to file",              "non", save_url),
        get_cmd("curl",     "Save curl output to file",             "non", save_curl),
        get_cmd("diff",     "Save git diff",                        "non", save_diff),
        get_cmd("ts",       "Get backup time stamp",                "non", get_time_stamp),
        get_cmd("gs",       "Save git status to file",              "non", save_git_status),
        get_cmd("uuid",     "Generate new uuid",                    "non", gen_uuid),
        get_cmd("sc",       "Save cmd output to file & open",       "non", save_cmd_and_open),
        get_cmd("gc",       "Copy and concat git status files",     "-m" , git_copy),
        get_cmd("red",      "Reduce to filenames",                  "non" , reduce_filenames),
        get_cmd("o",        "Open branch specifiec file",           "branch_name" , open_branch_ticket),
        get_cmd("sl",       "Slugify text pasted as parameter",     "non", slugify_cmd_line),
        get_cmd("ctc",      "Compare top commit with remote top",   "non", compare_top_commit),
        get_cmd("en",       "Enlist the branch",                    "non", enlist_branches),
        get_cmd("t",        "Open Jira Ticket",                     "non", open_jira_ticket),
        get_cmd("or",       "Open Repo",                            "non", open_repository),
        get_cmd("mock",     "Load all mocks",                       "non", load_all_mocks),
        get_cmd("am",       "Copy the amend code",                  "non", copy_amend),
        get_cmd("ame",      "Copy the amend code without edit",     "non", copy_amend_no_edit),
        get_cmd("rbt",      "Review board utility",                 "non", run_rbt_utility),
        get_cmd("push",     "Review board utility",                 "non", safe_push_remote_branch),
        get_cmd("merge-stg","Merge to Staging",                     "non", merge_to_staging),
        get_cmd("merge-master","Merge to Master",                   "non", merge_to_master)
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
