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
    buffer = {}

    for line in lines:
        if '=' in line:
            parts = line.split("=")
            if len(parts) > 1:
                name = parts[0]
                link = parts[1]
                buffer[name] = link

    return buffer

def search_for_links(term, name_link_map):
    search_results = {}
    index = 1

    for name in name_link_map:

        link = name_link_map[name]
        if term in name.lower() or term in link.lower():
            search_results[str(index)] = link
            index = index + 1

    return search_results

if __name__ == "__main__":

    arg1 = get_param(1)
    bookmarks_file = os.path.join(os.environ.get("HOME"), ".bookmarksv4.txt")
    bookmark_contents = read_file_contents(bookmarks_file)
    lines = bookmark_contents.split(NEW_LINE)
    lines = [line for line in lines if len(line.strip()) > 0]

    url_id = get_param(1)
    if url_id is None:
        for line in lines:
            print("\t\t%s..." % line[:100])
        err_exit()

    name_link_map = build_content(lines)
    # data = {'name': 'link', 'name2': 'link2'}

    if url_id in name_link_map:
        print("Opening Link: %s" % name_link_map[url_id])
        open_url_in_browser(name_link_map[url_id], get_params())
        exit()

    search_results = search_for_links(url_id, name_link_map)

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
