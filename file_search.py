import os
import sys
import re

def search(term, directory):
    expr = re.compile(build_term(term), re.M|re.I)
    for root, directories, filenames in os.walk(directory):
        for directory in directories:
            if (expr.match(directory) != None):
                print(os.path.join(root, directory))
        for filename in filenames:
            if (expr.match(filename) != None):
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

    directory = os.getcwd()

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
