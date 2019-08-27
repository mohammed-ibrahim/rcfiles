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
    url_map = {}

    for line in lines:
        parts = line.split(" ")
        if len(parts) == 2:
            url_map[parts[0]] = parts[1]
        else:
            print("Invalid url: %s" % line)

    url_id = get_param(1)

    if url_id is None or url_id not in url_map:
        for key in url_map:
            print("\t%s\t\t%s" % (key, url_map[key]))

        err_exit()

    open_url_in_browser(url_map[url_id])
