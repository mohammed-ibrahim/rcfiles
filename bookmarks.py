import webbrowser
import sys
import os
import re
from pytrie import StringTrie


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

def write_to_file(file_name, content):
    with open(file_name, "w") as file_pointer:
        file_pointer.write(content)

    print("File write complete: " + file_name)

def clean_string(line):
    return re.sub('\s+', ' ', line).strip()

def reform_line(line):
    line = clean_string(line)
    parts = line.split(" ")
    return "%s%s%s" % (parts[0].ljust(25), parts[1].ljust(35), parts[2])

def reform_file(bookmarks_file, lines):
    reformed_lines = []

    for line in lines:
        reformed_lines.append(reform_line(line))

    write_to_file(bookmarks_file, NEW_LINE.join(reformed_lines))

def build_ds(lines):
    primary_keys = {}
    links = []
    tag_map = {}

    for i in range(len(lines)):
        line = lines[i]
        parts = clean_string(line).split(" ")
        if len(parts) == 3:
            primary_key = parts[0]
            link = parts[2]
            primary_keys[primary_key] = [i]
            links.append(link)

            tags = parts[1]
            tags = tags.split(",")
            for tag in tags:
                if tag not in tag_map:
                    tag_map[tag] = []

                tag_map[tag].append(i)
        else:
            print("Invalid url: %s" % line)

    return {
        "primary_keys": primary_keys,
        "links": links,
        "tag_map": tag_map
    }

def build_trie_and_execute(map_to_search, prefix_term):
    trie = StringTrie()
    for key in map_to_search:
        trie[key] = key

    prefix_matches = trie.values(url_id)
    if len(prefix_matches) > 0:
        first_match = prefix_matches[0]
        index = map_to_search[first_match][0]
        open_url_in_browser(links[index], get_params())
        return True

    return False

if __name__ == "__main__":

    arg1 = get_param(1)
    bookmarks_file = os.path.join(os.environ.get("HOME"), ".bookmarks.txt")
    bookmark_contents = read_file_contents(bookmarks_file)
    lines = bookmark_contents.split(NEW_LINE)
    lines = [line for line in lines if len(line.strip()) > 0]

    if "-r" == arg1 or "--reform" == arg1:
        print("formatting bookmark file.")
        reform_file(bookmarks_file, lines)
        print("bookmark file formatted successfully.")
        sys.exit(0)

    response = build_ds(lines)
    primary_keys = response['primary_keys']
    links = response['links']
    tag_map = response['tag_map']

    url_id = get_param(1)
    if url_id is None:
        for line in lines:
            print("\t\t%s..." % line[:100])
        err_exit()

    # 1. direct search primary key
    # 2. direct search tag
    # 3. prefix primary key
    # 4. prefix search tag

    if url_id in primary_keys:
        index = primary_keys[url_id][0]
        open_url_in_browser(links[index], get_params())
        exit()

    if url_id in tag_map:
        first_link_of_tag = tag_map[url_id][0]
        open_url_in_browser(links[first_link_of_tag], get_params())
        exit()


    prefix_found_for_primary_keys = build_trie_and_execute(primary_keys, url_id)
    if prefix_found_for_primary_keys:
        exit()

    prefix_found_for_tags = build_trie_and_execute(tag_map, url_id)
    if prefix_found_for_tags:
        exit()

    print("No suggestions for: %s" % url_id)
