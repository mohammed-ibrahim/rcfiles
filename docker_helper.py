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
        err_exit()

    return out

def s_run_process_and_get_output(s_cmd, exit_on_failure=False):
    return run_process_and_get_output(s_cmd.split(" "), exit_on_failure)

def get_required_container_id():
    ps = s_run_process_and_get_output("docker ps", True)
    lines = ps.split("\n")
    lines = [line for line in lines if len(line.strip()) > 0]
    lines = [re.sub('\s+', ' ',line) for line in lines]
    lines = lines[1:]

    for line in lines:
        parts = line.split(" ")
        container_id = parts[0]
        docker_name = parts[1]

        for pri_keywords in PRIORITY_KEYWORDS:
            if docker_name.startswith(pri_keywords):
                print("Found docker for: %s" % (docker_name))
                return container_id

        print("None of dockers found fro keywords: %s" % (",".join(PRIORITY_KEYWORDS)))
        err_exit()

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

if __name__ == "__main__":
    container_id = get_required_container_id()
    print("container id is: %s" % container_id)

    param = get_param(1)

    if param is not None:
        output = s_run_process_and_get_output("docker %s %s" % (param, container_id))
        print(output)
