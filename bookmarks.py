import webbrowser
import sys
import os

def open_url_in_browser(url):
    webbrowser.open(url, new=0, autoraise=True)

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

def err_exit():
    sys.exit(1)

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

NEW_LINE = "\n"

if __name__ == "__main__":

    bookmarks_file = os.path.join(os.environ.get("HOME"), ".bookmarks.txt")
    bookmark_contents = read_file_contents(bookmarks_file)
    lines = bookmark_contents.split(NEW_LINE)
    lines = [line for line in lines if len(line.strip()) > 0]

    index_list = []
    command_list = []

    for line in lines:
        parts = line.split(" ")
        if len(parts) == 2:
            bmk_key = parts[0]
            bmk_link = parts[1]
            index_list.append(bmk_key)
            command_list.append([bmk_key, bmk_link])
        else:
            print("Invalid url: %s" % line)

    url_id = get_param(1)

    if url_id is None or url_id not in index_list:
        for bmk in command_list:
            bmk_key = bmk[0]
            bmk_link = bmk[1]
            print("\t%s - %s..." % (bmk_key.ljust(25), bmk_link[:50]))
        err_exit()

    index = index_list.index(url_id)
    open_url_in_browser(command_list[index][1])
