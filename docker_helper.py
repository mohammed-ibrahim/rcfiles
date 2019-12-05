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

def as_str(text):
    if str == type(text):
        return text

    return text.decode("utf-8")

def fetch_all_container_ids():
    result = as_str(s_run_process_and_get_output("docker ps -q", True))
    result.strip("\n").strip()

    if len(result) < 1:
        return []

    return [id for id in result.split("\n") if len(id.strip()) > 0]

def halt_all():
    all_running_container_ids = fetch_all_container_ids()
    print("Stopping one by one: %s" % " :: ".join(all_running_container_ids))

    for id in all_running_container_ids:
        s_run_process_and_get_output("docker stop %s" % id, True)

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

    param = get_param(1)

    if param in ["halt", "h"]:
        halt_all()
    elif param in ["log", "logs", "l"]:
        container_id = get_required_container_id()
        text = "docker logs -f %s" % (container_id)
        run_command(text)
    else:
        print("Nothing doing...")
