import os
import sys
import re

def search(term, directory):
    term = build_term(term)
    for root, directories, filenames in os.walk(directory):
        for directory in directories:
            if (re.match(term, directory, re.M|re.I) != None):
                print(os.path.join(root, directory))
        for filename in filenames:
            if (re.match(term, filename, re.M|re.I) != None):
                print(os.path.join(root,filename))
    return

def build_term(term):
    if term[:1] == "*":
        term = term[1:]

    if term[-1:] == "*":
        term = term[:-1]

    term = "*" + term + "*"
    term = term.replace("*", "(.*)")

    return term

def get_term():
    if len(sys.argv) not in [2, 3]:
        print('Usage: <program> <search_string> [<directory>]')
        sys.exit()

    directory = './'

    if len(sys.argv) == 3:
        directory = sys.argv[2]

    if (os.path.isdir(directory) == False):
        print("Invalid directory: " + directory)
        sys.exit()

    return (sys.argv[1], directory)

if __name__ == '__main__':
    (term, directory) = get_term()
    
    build_term(term)
    if term != None:
        search(term, directory)
