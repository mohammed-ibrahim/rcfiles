import os
import sys

def search(term):
    term = term.lower()
    for root, directories, filenames in os.walk('./'):
        for directory in directories:
                #print directory   #os.path.join(root, directory) 
                if (directory.lower().find(term) != -1):
                    print(os.path.join(root, directory))
        for filename in filenames: 
                #print filename #os.path.join(root,filename) 
                if (filename.lower().find(term) != -1):
                    print(os.path.join(root,filename))
    return


def get_term():
    if len(sys.argv) not in [2]:
        print('Usage: <program> <search_string>')
        return None

    return sys.argv[1]

if __name__ == '__main__':
    term = get_term()
    
    if term != None:
        search(term)
