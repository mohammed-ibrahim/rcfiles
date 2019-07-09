import subprocess
import os
import sys


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


if __name__ == "__main__":

    if len(sys.argv) < 2:
        print("usage: 1 :: build gs")
        print("usage: 2 :: build files [space-seperated-files]")
        print("usage: 3 :: build files from last commit")
        sys.exit(1)

    mode = sys.argv[1]

    if mode not in ["gs", "files", "last_commit"]:
        print("usage: 1 :: build gs")
        print("usage: 2 :: build files [space-seperated-files]")
        print("usage: 3 :: build last_commit")
        sys.exit(1)

    deploy_suffix = os.environ.get('SCP_DEPLOY_LOCATION', None)
    if deploy_suffix is None:
        print("SCP_DEPLOY_LOCATION is not set")
        sys.exit(1)

    print("Deploy suffix: %s" % deploy_suffix)
    files = []

    if mode == "gs":

        process_output = s_run_process_and_get_output("git status")
        files = get_modified_files_from_git_status(process_output)

    elif mode == "files":

        if len(sys.argv) < 3:
            print("Insufficient files")
            sys.exit(1)

        for i in range(2, len(sys.argv)):
            files.append(sys.argv[i])

    elif mode == "last_commit":
        last_commit_message = s_run_process_and_get_output("git log -1")
        commit_id = last_commit_message.split("\n")[0].split(" ")[1]
        print("fetching files from commit id: " + commit_id)
        last_commit_list_cmd = "git diff-tree --no-commit-id --name-only -r %s" % commit_id
        files_in_last_commit = s_run_process_and_get_output(last_commit_list_cmd)

        for file_c in files_in_last_commit.split("\n"):
            if len(file_c) > 0:
                files.append(file_c)

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
        cmd_list.append(c2)


    cmd_list.append("cd %s" % cwd)
    print("\n\n---------------------------------------------------------------------\n\n")
    print(" && \n".join(cmd_list))
    print("\n\n---------------------------------------------------------------------\n\n")
    os.chdir(cwd)
