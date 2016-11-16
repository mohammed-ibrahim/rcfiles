import os
import sys
from os.path import basename
import time
import shutil
import datetime

class DirectoryIndexer(object):
    file_name = ""
    items = list()

    def __init__(self, arg):
        self.file_name = arg
        items = list()
        
    max_items = 500

    def flush(self):
        if len(self.items) < 1:
            return

        with open(self.file_name, 'a+') as file_handle:
            for item in self.items:
                file_handle.write(item)
                file_handle.write('\n')

            self.items = list()

    def add_item(self, item):
        self.items.append(item)

        if (len(self.items) > self.max_items):
            self.flush()


def index(search_dir, upload_file_path):
    indexer = DirectoryIndexer(upload_file_path)
    valid_file_types=['php', 'py', 'scala', 'html', 'java', 'xml', 'yml', 'ju', 'ini', 'c']
    items_added = 0

    for root, directories, filenames in os.walk(search_dir):
        for filename in filenames:
            (fname, ext) =  os.path.splitext(filename)
            if not ext is None and len(ext) > 0:
                ext = ext.lower()[1:]
            if ext in valid_file_types:
                indexer.add_item(os.path.join(root,filename))
                items_added += 1

    indexer.flush()
    return items_added

def get_directory_list():
    if len(sys.argv) not in [3]:
        print('Usage: <program> <input_directories> <directory>')
        sys.exit()

    dirs = sys.argv[1].split(":")
    out_file = sys.argv[2] 

    for directory in dirs:
        if os.path.isdir(directory) == False:
            print("Invalid directory: " + directory)
            sys.exit()
        #else:
        #    print("Valid dir: " + directory)

    if os.path.exists(out_file):
        if os.path.isdir(out_file):
            print("Invalid index file: " + out_file)
            sys.exit()

    return (dirs, out_file)

if __name__ == '__main__':
    start_at = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print("Job started at: " + start_at)

    (dirs, out_file) = get_directory_list()
    temp_file = out_file + str(int(time.time()))

    for directory in dirs:
        files_indexed = index(directory, temp_file)
        print("Directory: " + directory + " (" + str(files_indexed) + ")")

    shutil.move(temp_file, out_file)

    end_at = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    print("Job finished at: " + end_at)
