import subprocess
import sys

def run_sysc(command_list, exit_on_failure=False):
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        sys.exit(1)

    return out

def s_run_sysc(s_cmd, exit_on_failure=False):
    return run_sysc(s_cmd.split(" "), exit_on_failure)

def clear_line(line):
    line = line.replace("modified:", "").replace("\t", "").replace(" ", "")
    return line

def get_distinct_files(text):
    lines = [x for x in text.split("\n") if "modified:" in x]
    return [clear_line(g) for g in lines]

if __name__ == "__main__":
    res = s_run_sysc("git status")
    print(get_distinct_files(res))
