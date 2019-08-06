import subprocess
import json
import os
import sys
import datetime
import time
import pyperclip
import re
import requests


def run_interactive(exe):
    p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while(True):
        # returns None while subprocess is running
        retcode = p.poll()
        line = p.stdout.readline()
        print(line)

        if retcode is not None:
            break

def run_process_and_get_output(command_list, exit_on_failure=False):
    print("Executing ::: %s" % " ".join(command_list))
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        err_exit()

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

def get_distinct_submodule_locations(files):
    src_files = [x for x in files if "src/main" in x]
    src_files = list(set(src_files))
    submodule_locations = set()

    for sfile in src_files:
        submodule_root_path = sfile[0:sfile.index("src/main")]
        pom_file = os.path.join(submodule_root_path, "pom.xml")

        if os.path.isfile(pom_file):
            submodule_locations.add(submodule_root_path)

    return list(submodule_locations)

def get_build_and_deploy_statements(proj_dir, deploy_suffix):
    os.chdir(proj_dir)
    # s_run_process_and_get_output("mvn -DskipTests=true -Dcheckstyle.skip install", exit_on_failure=True)
    cmd = "mvn -DskipTests=true -Dcheckstyle.skip install"
    target_dir = os.path.join(proj_dir, "target")
    jars = [a for a in os.listdir(target_dir) if a.endswith(".jar") and not a.endswith("tests.jar")]

    if len(jars) > 0:
        required_jar = jars[0]
    else:
        required_jar = "jar-location-not-found.jar"

    jar_full_path = os.path.join(proj_dir, "target", required_jar)

    cmd2 = None
    if deploy_suffix is not None:
        cmd2 = "scp %s %s" % (jar_full_path, deploy_suffix)
        #s_run_process_and_get_output("scp %s %s" % (jar_full_path, deploy_suffix), True)

    return (cmd, cmd2)

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

def get_cmd(code, desc):
    return {
        "code": code,
        "desc": desc
    }

NEW_LINE = "\n"
GS = get_cmd('gs', 'get build command from git status')
FILES = get_cmd('files', 'get build command from manually supplied comma seperated files')
LAST_COMMIT = get_cmd('lc', 'get build command from changes in last commit')
UPDATE_BRANCH = get_cmd('ub', 'get update branch command list')
TS = get_cmd('ts', 'get time stamp for backup location')
HEAD = get_cmd('head', 'save last commit diff & get open link')
LHEAD = get_cmd('lhead', 'list files modified/added in last commit')
DIFF = get_cmd('diff', 'save git diff & get open link')
GP = get_cmd('gp', 'git copy modified and new file to clipboard, or specified file.')
STORE_COMMIT_ID = get_cmd('sci', 'record commit link to db')
CFG = get_cmd('cfg', 'show local config for current branch/story')
URL = get_cmd('url', 'Save url [GET] to local file and copy file link.')
CURL = get_cmd('curl', 'Save Curl [GET] to local file and copy file link.')
AN = get_cmd('an', 'Annotate git status files')


PRIMARY_OPERATIONS = [
    GS, FILES, LAST_COMMIT, UPDATE_BRANCH, TS, HEAD, LHEAD, DIFF, GP, STORE_COMMIT_ID, CFG, URL, CURL, AN
]

def get_ts():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')

def get_current_branch():
    branch_details = s_run_process_and_get_output("git branch")
    current_branch = [x for x in branch_details.split(NEW_LINE) if "*" in x][0]
    return current_branch[2:]

def get_cwd_name():
    cwd = os.getcwd()
    path_parts = cwd.split("/")
    cwd_name = path_parts.pop().strip()
    return cwd_name

def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

def load_or_create_config(file_path):

    parsed = {}

    if os.path.isfile(file_path):
        contents = read_file_contents(file_path)
        parsed = json.loads(contents)

    return parsed

def get_repo_url():
    process_output = s_run_process_and_get_output('git config remote.origin.url')
    return 'https://' + process_output.split("@")[1].replace(":", "/")[:-5]

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def slugify(text):
    output = re.sub(r'\W+', '-', text)
    return output.lower()

def get_qualifier_with_custom_ctx(ctx, extension):
    ctx = slugify(ctx)
    local_directory = pull_env_var('LOCAL_BACKUP_DIR')
    return os.path.join(local_directory, "%s-%s.%s" % (ctx, get_ts(), extension))

def get_qualifier_with_ctx():
    ctx = get_param(2)
    if ctx is None:
        ctx = get_cwd_name()
    else:
        ctx = slugify(ctx)

    local_directory = pull_env_var('LOCAL_BACKUP_DIR')
    return os.path.join(local_directory, "%s-%s" % (ctx, get_ts()))

def display_primary_operations():
    primary_operation_codes = [x['code'] for x in PRIMARY_OPERATIONS]
    print("usage: :: a [%s]" % (",".join(primary_operation_codes)))
    for cmd in PRIMARY_OPERATIONS:
        print("\t\t %s \t\t[%s]" % (cmd['code'], cmd['desc']))

def pull_env_var(key):
    env_value = os.environ.get(key, None)
    if env_value is None:
        print("%s environment variable is not set" % key)
        err_exit()

    return env_value

def execute_curl_command():
    args_len = len(sys.argv)
    url = None
    headers = {}
    extension = "txt"

    for i in range(2, args_len):
        part = sys.argv[i]

        if part.lower() == 'curl':
            continue

        if part == "-H":
            next_part = sys.argv[i+1]
            parts = next_part.split(": ")
            headers[parts[0]] = parts[1]

        if part.lower() == "-e":
            extension = sys.argv[i+1]

        if part.startswith("http"):
            url = part

    if url is None:
        print("Invalid command")
        err_exit()

    file_name = get_qualifier_with_custom_ctx("curl-save", extension)
    req = requests.get(url, headers = headers)
    write_to_file(file_name, req.content)
    pyperclip.copy("vi %s" % file_name)

def show_mvn_build_cmd(files, add_scp):
    for f in files:
        print(f)

    dist_files = get_distinct_submodule_locations(files)

    if len(dist_files) == 0:
        print("changes doesn't have any deployable code modifications")
        err_exit()

    cwd = os.getcwd()
    cmd_list = []
    for cur_dir in dist_files:
        full_path = os.path.join(cwd, cur_dir)
        c1, c2 = get_build_and_deploy_statements(full_path, deploy_suffix)

        cmd_list.append("cd %s" % full_path)
        cmd_list.append(c1)
        if add_scp:
            cmd_list.append(c2)

    cmd_list.append("cd %s" % cwd)
    print("\n\n---------------------------------------------------------------------\n\n")
    print(" && \n".join(cmd_list))
    print("\n\n---------------------------------------------------------------------\n\n")
    os.chdir(cwd)

def err_exit():
    sys.exit(1)

def exit_app():
    sys.exit(0)

if __name__ == "__main__":

    primary_operation_codes = [x['code'] for x in PRIMARY_OPERATIONS]
    mode = get_param(1)
    if mode is None or mode not in primary_operation_codes:
        display_primary_operations()
        err_exit()

    add_scp = True
    if "-n" in sys.argv:
        add_scp = False

    deploy_suffix = pull_env_var('SCP_DEPLOY_LOCATION')
    local_file_db_dir = pull_env_var('LOCAL_FILE_DB_DIR')

    if mode == GS['code']:

        process_output = s_run_process_and_get_output("git status")
        files = get_modified_files_from_git_status(process_output)
        show_mvn_build_cmd(files, add_scp)
        exit_app()

    elif mode == FILES['code']:

        if len(sys.argv) < 3:
            print("Insufficient files")
            err_exit()

        files = []
        for i in range(2, len(sys.argv)):
            files.append(sys.argv[i])

        show_mvn_build_cmd(files, add_scp)
        exit_app()

    elif mode == LAST_COMMIT['code']:
        last_commit_message = s_run_process_and_get_output("git log -1")
        commit_id = last_commit_message.split("\n")[0].split(" ")[1]
        print("fetching files from commit id: " + commit_id)
        last_commit_list_cmd = "git diff-tree --no-commit-id --name-only -r %s" % commit_id
        files_in_last_commit = s_run_process_and_get_output(last_commit_list_cmd)

        files = []
        for file_c in files_in_last_commit.split("\n"):
            if len(file_c) > 0:
                files.append(file_c)

        show_mvn_build_cmd(files, add_scp)
        exit_app()

    elif mode == UPDATE_BRANCH['code']:
        current_branch = get_param(2)

        if current_branch is None:
            current_branch = get_current_branch()

        current_user_details = s_run_process_and_get_output("whoami")
        current_user = current_user_details.split(NEW_LINE)[0]
        required_url = "%s/commits/topic/%s/%s" % (get_repo_url(), current_user, current_branch)

        cmd = update_branch_template % (current_user, current_branch, required_url, current_branch, current_user, current_branch, current_user, current_branch)
        print(cmd)
        exit_app()

    elif mode == TS['code']:
        fully_qualified_path_for_backup = get_qualifier_with_ctx()
        pyperclip.copy(fully_qualified_path_for_backup)
        print("\n\n%s - copied to clipboard\n\n" % fully_qualified_path_for_backup)
        exit_app()

    elif mode == HEAD['code']:
        head_diff = s_run_process_and_get_output('git show HEAD')
        file_name = "%s.diff" % get_qualifier_with_ctx()
        write_to_file(file_name, head_diff)
        pyperclip.copy("vi %s" % file_name)
        exit_app()

    elif mode == LHEAD['code']:
        lhead_diff = s_run_process_and_get_output('git diff-tree --no-commit-id --name-only -r HEAD')
        all_lines = [line for line in lhead_diff.split("\n") if len(line) > 0]
        print("\n\n%s\n\n" % (" ".join(all_lines)))
        print("::\n\n")
        for line in all_lines:
            print(line)
        print("\n\n::\n\n")
        exit_app()

    elif mode == DIFF['code']:
        git_diff = s_run_process_and_get_output('git diff')
        file_name = "%s.diff" % get_qualifier_with_ctx()
        write_to_file(file_name, git_diff)
        pyperclip.copy("vi %s" % file_name)
        exit_app()

    elif mode == GP['code']:
        process_output = s_run_process_and_get_output('git status -s')
        files = [x[3:] for x in process_output.split("\n") if len(x.strip()) > 0]
        param = get_param(2)
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
        exit_app()

    elif mode == STORE_COMMIT_ID['code']:
        last_commit_id = s_run_process_and_get_output('git rev-parse HEAD').strip()
        required_url = get_repo_url() + '/commit/' + last_commit_id
        file_name = get_cwd_name() + "-" + get_current_branch()
        file_path = os.path.join(local_file_db_dir, file_name)
        print("%s %s" % (file_name, file_path))
        content = load_or_create_config(file_path)

        if 'commit_links' not in content:
            content['commit_links'] = []

        content['commit_links'].append({
                "url": required_url,
                "time": get_ts()
            })
        write_to_file(file_path, json.dumps(content, indent=4))
        exit_app()

    elif mode == CFG['code']:

        file_name = get_cwd_name() + "-" + get_current_branch()
        file_path = os.path.join(local_file_db_dir, file_name)
        if os.path.isfile(file_path):
            contents = read_file_contents(file_path)
            print("\n\n%s\n\n" % contents)
        else:
            print("\n\nCONFIG NOT FOUND\n\n")

        exit_app()

    elif mode == URL['code']:
        url = get_param(2)
        if url is None:
            print("usage: a %s <url>" % (URL['code']))
            err_exit()
            err_exit()

        file_name = get_qualifier_with_custom_ctx("url-save", "txt")
        req = requests.get(url)
        write_to_file(file_name, req.content)
        pyperclip.copy("vi %s" % file_name)
        exit_app()

    elif mode == CURL['code']:
        #1 Parse url & headers
        #2 make call
        execute_curl_command()
        exit_app()

    elif mode == AN['code']:
        modified_files = s_run_process_and_get_output("git ls-files -m").split("\n")
        untracked_files = s_run_process_and_get_output("git ls-files -o").split("\n")

        all_files = []

        for file in modified_files:
            if len(file) > 0:
                all_files.append(file)

        for file in untracked_files:
            if len(file) > 0:
                all_files.append(file)

        selection = get_param(2)

        if selection is None:
            if len(all_files) > 0:
                print("\n\n")
                for index in range(len(all_files)):
                    print("%d %s" % (index, all_files[index]))
                print("\n\n")
            else:
                print("\n\nNo files found !!!\n\n")
        elif selection.lower() == "all":
            pyperclip.copy(" ".join(all_files))
        else:
            pyperclip.copy(all_files[int(selection)])

        exit_app()
    else:
        print("Invalid mode : %s" % mode)
        err_exit()
