from __future__ import print_function # Only Python 2.x
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
import shlex

PRIORITY_KEYWORDS = [
    "authcontrol"
]

def err_exit():
    sys.exit(1)

def run_process_and_get_output(command_list, exit_on_failure=False):
    print("Executing ::: %s" % " ".join(command_list))
    p = subprocess.Popen(command_list, stdout=subprocess.PIPE,   stderr=subprocess.PIPE)
    out, err = p.communicate()

    if exit_on_failure and len(err) > 0:
        print("Process failure: %s" % err)
        err_exit()


    return out.decode("utf-8")

def s_run_process_and_get_output(s_cmd, exit_on_failure=False):
    return run_process_and_get_output(s_cmd.split(" "), exit_on_failure)

def get_last_part_of_pwd():
    text = os.path.basename(os.path.normpath(os.getcwd()))
    text = text.replace("vidm_", "")
    return text

def get_required_container_id():
    cmd_text = 'docker ps -a -q --filter=name=%s' % get_last_part_of_pwd()
    print("ct")
    ps = s_run_process_and_get_output(cmd_text, True)
    ps = str(ps)
    print("cz")
    print("process output = %s" % ps)
    ps = ps.strip('\n').strip()
    print("---%s---" % str(ps))
    if len(ps) > 0:
        return ps

    print("Couldn't find docker name for given folder")
    err_exit()

    # for line in lines:
    #     parts = line.split(" ")
    #     container_id = parts[0]
    #     docker_name = parts[1]
    #
    #     for pri_keywords in PRIORITY_KEYWORDS:
    #         if docker_name.startswith(pri_keywords):
    #             print("Found docker for: %s" % (docker_name))
    #             return container_id
    #
    #     print("None of dockers found fro keywords: %s" % (",".join(PRIORITY_KEYWORDS)))
    #     err_exit()

# def interactive_execute(cmd):
#     popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
#     for stdout_line in iter(popen.stdout.readline, ""):
#         print(stdout_line)
#
#     popen.stdout.close()
#     return_code = popen.wait()
#     if return_code:
#         raise subprocess.CalledProcessError(return_code, cmd)


def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None


def run_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.decode("utf-8").strip())
    rc = process.poll()
    return rc

if __name__ == "__main__":
    container_id = get_required_container_id()
    print("container id is: %s" % container_id)

    param = get_param(1)


    if "tailf" == param:
        text = "docker logs -f %s" % (container_id)
        print(text)
        pyperclip.copy(text)
        # interactive_execute("docker logs -f %s" % (container_id))
        # 78f14341566d
        # interactive_execute("docker logs -f 78f14341566d")
        # print("uyess")
    elif param is not None:
        output = s_run_process_and_get_output("docker %s %s" % (param, container_id))
        print(output)
