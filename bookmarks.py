import webbrowser
import sys
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
    index_list = []
    command_list = []
    tag_map = {}

    for line in lines:
        parts = clean_string(line).split(" ")
        if len(parts) == 3:
            bmk_key = parts[0]
            bmk_tags = parts[1]
            bmk_link = parts[2]
            index_list.append(bmk_key)
            command_list.append([bmk_key, bmk_tags, bmk_link])

            tags = bmk_tags.split(",")
            for tag in tags:
                if tag not in tag_map:
                    tag_map[tag] = []

                tag_map[tag].append(bmk_link)
        else:
            print("Invalid url: %s" % line)

    return {
        "index_list": index_list,
        "command_list": command_list,
        "tag_map": tag_map
    }

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
    index_list = response['index_list']
    command_list = response['command_list']
    tag_map = response['tag_map']

    url_id = get_param(1)

    if url_id is None:
        for bmk in command_list:
            bmk_key = bmk[0]
            bmk_tags = bmk[1]
            bmk_link = bmk[2]
            print("\t%s %s - %s..." % (bmk_key.ljust(25), bmk_tags.ljust(25), bmk_link[:50]))
        err_exit()

    # 1. direct search primary key
    # 2. direct search tag
    # 3. prefix primary key
    # 4. prefix search tag

    if url_id in index_list:
        index = index_list.index(url_id)
        open_url_in_browser(command_list[index][2], get_params())
        exit()

    if url_id in tag_map:
        first_link_of_tag = tag_map[url_id][0]
        open_url_in_browser(first_link_of_tag, get_params())
        exit()

    print("not found")
