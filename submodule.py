import subprocess
import json
import os
import sys
import datetime
import time
import pyperclip
import re


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


PRIMARY_OPERATIONS = [
    GS, FILES, LAST_COMMIT, UPDATE_BRANCH, TS, HEAD, LHEAD, DIFF, GP, STORE_COMMIT_ID
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
    print("--------------------------------------------------------------")
    print(file_path)
    print("--------------------------------------------------------------")

    parsed = {}

    if os.path.isfile(file_path):
        contents = read_file_contents(file_path)
        parsed = json.loads(contents)

    return parsed

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def slugify(text):
    output = re.sub(r'\W+', '-', text)
    return output

def get_qualifier_with_ctx():
    ctx = get_param(2)
    if ctx is None:
        ctx = get_cwd_name()
    else:
        ctx = slugify(ctx)

    local_directory = os.environ.get('LOCAL_BACKUP_DIR', None)
    if local_directory is None:
        print("LOCAL_BACKUP_DIR is not set")
        sys.exit(1)

    return os.path.join(local_directory, "%s-%s" % (ctx, get_ts()))

if __name__ == "__main__":

    primary_operation_codes = [x['code'] for x in PRIMARY_OPERATIONS]
    if len(sys.argv) < 2:
        print("usage: :: build [%s]" % (",".join(primary_operation_codes)))
        for cmd in PRIMARY_OPERATIONS:
            print("\t\t %s \t\t[%s]" % (cmd['code'], cmd['desc']))
        sys.exit(1)

    mode = sys.argv[1]

    if mode not in primary_operation_codes:
        print("usage: 1 :: \t\t %s [-n]" % GS['code'])
        print("usage: 2 :: \t\t %s [space-seperated-files] [-n]" % FILES['code'])
        print("usage: 3 :: \t\t %s [-n]" % LAST_COMMIT['code'])
        print("usage: 4 :: \t\t %s" % UPDATE_BRANCH['code'])
        print("usage: 5 :: \t\t %s" % TS['code'])
        sys.exit(1)

    add_scp = True
    if "-n" in sys.argv:
        add_scp = False

    deploy_suffix = os.environ.get('SCP_DEPLOY_LOCATION', None)
    if deploy_suffix is None:
        print("SCP_DEPLOY_LOCATION is not set")
        sys.exit(1)

    print("Deploy suffix: %s" % deploy_suffix)

    local_file_db_dir = os.environ.get('LOCAL_FILE_DB_DIR', None)
    if local_file_db_dir is None:
        print("LOCAL_FILE_DB_DIR is not set")
        sys.exit(1)

    print("Local file db directory: %s" % local_file_db_dir)

    files = []

    if mode == GS['code']:

        process_output = s_run_process_and_get_output("git status")
        files = get_modified_files_from_git_status(process_output)

    elif mode == FILES['code']:

        if len(sys.argv) < 3:
            print("Insufficient files")
            sys.exit(1)

        for i in range(2, len(sys.argv)):
            files.append(sys.argv[i])

    elif mode == LAST_COMMIT['code']:
        last_commit_message = s_run_process_and_get_output("git log -1")
        commit_id = last_commit_message.split("\n")[0].split(" ")[1]
        print("fetching files from commit id: " + commit_id)
        last_commit_list_cmd = "git diff-tree --no-commit-id --name-only -r %s" % commit_id
        files_in_last_commit = s_run_process_and_get_output(last_commit_list_cmd)

        for file_c in files_in_last_commit.split("\n"):
            if len(file_c) > 0:
                files.append(file_c)

    elif mode == UPDATE_BRANCH['code']:
        current_branch = get_current_branch()

        current_user_details = s_run_process_and_get_output("whoami")
        current_user = current_user_details.split(NEW_LINE)[0]

        cmd = update_branch_template % (current_user, current_branch, current_branch, current_user, current_branch, current_user, current_branch)
        print(cmd)
        sys.exit(0)

    elif mode == TS['code']:
        fully_qualified_path_for_backup = get_qualifier_with_ctx()
        pyperclip.copy(fully_qualified_path_for_backup)
        print("\n\n%s - copied to clipboard\n\n" % fully_qualified_path_for_backup)
        sys.exit(0)

    elif mode == HEAD['code']:
        head_diff = s_run_process_and_get_output('git show HEAD')
        file_name = "%s.diff" % get_qualifier_with_ctx()
        write_to_file(file_name, head_diff)
        pyperclip.copy("vi %s" % file_name)
        sys.exit(0)

    elif mode == LHEAD['code']:
        lhead_diff = s_run_process_and_get_output('git diff-tree --no-commit-id --name-only -r HEAD')
        all_lines = [line for line in lhead_diff.split("\n") if len(line) > 0]
        print("\n\n%s\n\n" % (" ".join(all_lines)))
        print("::\n\n")
        for line in all_lines:
            print(line)
        print("\n\n::\n\n")
        sys.exit(0)

    elif mode == DIFF['code']:
        git_diff = s_run_process_and_get_output('git diff')
        file_name = "%s.diff" % get_qualifier_with_ctx()
        write_to_file(file_name, git_diff)
        pyperclip.copy("vi %s" % file_name)
        sys.exit(0)

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
        sys.exit(0)

    elif mode == STORE_COMMIT_ID['code']:
        process_output = s_run_process_and_get_output('git config remote.origin.url')
        last_commit_id = s_run_process_and_get_output('git rev-parse HEAD').strip()
        required_url = 'https://' + process_output.split("@")[1].replace(":", "/")[:-5] + '/commit/' + last_commit_id
        file_name = get_cwd_name() + "-" + get_current_branch()
        file_path = os.path.join(local_file_db_dir, file_name)
        print("%s %s" % (file_name, file_path))
        content = load_or_create_config(file_path)

        if 'commit_links' not in content:
            content['commit_links'] = []

        content['commit_links'].append(required_url)
        write_to_file(file_path, json.dumps(content, indent=4))
        sys.exit(0)

    else:
        print("Invalid mode : %s" % mode)
        sys.exit(1)

    for f in files:
        print(f)

    dist_files = get_distinct_submodule_locations(files)

    if len(dist_files) == 0:
        print("changes doesn't have any deployable code modifications")
        sys.exit(1)

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
