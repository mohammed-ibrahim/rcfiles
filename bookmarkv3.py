import webbrowser
import sys
import json
import os
import re


def open_url_in_browser(url, params):
    if "-f" in params:
        webbrowser.get('firefox').open_new_tab(url)
    else:
        webbrowser.open(url, new=0, autoraise=True)

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def err_exit():
    sys.exit(1)

def exit():
    sys.exit(0)

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

NEW_LINE = "\n"

def get_params():
    cmd_list = []
    for i in range(2, len(sys.argv)):
        cmd = sys.argv[i]
        cmd_list.append(cmd)
    return cmd_list

def build_content(lines):
    context = None
    buffer = []

    b_name = None
    b_tags = None
    b_link = None

    for line in lines:
        if line.startswith("name="):
            if context is not None:
                buffer.append({'name': b_name, 'tags': b_tags, 'link': b_link})

            name = line[5:]
            context = name
            b_name = name

        if line.startswith("tags="):
            tag_text = line[5:].strip()

            if len(tag_text) > 0:
                b_tags = tag_text.split(",")

        if line.startswith("link="):
            link_text = line[5:].strip()

            if len(link_text) > 0:
                b_link = link_text

    buffer.append({'name': b_name, 'tags': b_tags, 'link': b_link})
    return buffer

def build_name_vs_link_map(data):
    name_vs_link_map = {}

    for item in data:
        name = item['name']
        link = item['link']
        name_vs_link_map[name] = link

    return name_vs_link_map

def tag_search_matches(term, tags):
    if term in tags:
        return True

    for tag in tags:
        if term in tag:
            return True

    return False

def search_for_links(term, data):
    search_results = {}
    index = 1

    for item in data:
        if tag_search_matches(term, item['tags']) or term in item['link'].lower():
            search_results[str(index)] = item['link']
            index = index + 1

    return search_results

if __name__ == "__main__":

    arg1 = get_param(1)
    bookmarks_file = os.path.join(os.environ.get("HOME"), ".bookmarksv2.txt")
    bookmark_contents = read_file_contents(bookmarks_file)
    lines = bookmark_contents.split(NEW_LINE)
    lines = [line for line in lines if len(line.strip()) > 0]

    url_id = get_param(1)
    if url_id is None:
        for line in lines:
            print("\t\t%s..." % line[:100])
        err_exit()

    data = build_content(lines)
    # data looks like below
    # [
    #     {
    #         "link": "https://jenkins-hzn.eng.vmware.com/jenkins/view/Pre-Commit/job/horizon-workspace-pre-commit-unit-and-server-tests-ALL/build?delay=0sec",
    #         "name": "precommit-new",
    #         "tags": [
    #             "buildpre",
    #             "newpre",
    #             "pcn"
    #         ]
    #     },
    #     {
    #         "link": "https://jenkins-hzn.eng.vmware.com/jenkins/job/saas-pipeline-precommit/",
    #         "name": "precommit",
    #         "tags": [
    #             "pc"
    #         ]
    #     }
    # ]
    name_vs_link_map = build_name_vs_link_map(data)

    if url_id in name_vs_link_map:
        print("Opening Link: %s" % name_vs_link_map[url_id])
        open_url_in_browser(name_vs_link_map[url_id], get_params())
        exit()

    search_results = search_for_links(url_id, data)

    if len(search_results) < 1:
        print("No results found for: " + url_id)
        exit()

    if len(search_results) == 1:
        print("Opening Link: %s" % search_results["1"])
        open_url_in_browser(search_results["1"], get_params())
        exit()

    # Search results are more than 1, so interactive search.

    if len(url_id) < 3:
        print("Search term needs to be more than 2 chars")
        err_exit()

    print("Total number of results: %d \n\n" % len(search_results))
    for i in range(len(search_results)):
        index = str(i+1)
        print("%s - %s" % (index, search_results[index]))

    print("hit '0' to quit.\n\n")
    user_input = input("Please select file number: ")
    user_input = str(user_input).strip()

    if user_input in ['q', 'Q', '0']:
        exit()

    print("Selected: " + user_input)
    if user_input not in search_results:
        print("%s is not mentioned in the search results." % str(user_input))
        err_exit()
    else:
        print("Opening Link: %s" % search_results[user_input])
        open_url_in_browser(search_results[user_input], get_params())
        exit()
