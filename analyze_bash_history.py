import os

def read_file_contents(file_path):
    contents = None
    with open(file_path, "r") as file_pointer:
        contents = file_pointer.read()

    return contents

def sort_fun(list_a, list_b):
    # return list_a[0] - list_b[0]
    # return list_b[0] - list_a[0]
    return 1

if __name__ == "__main__":
    history_file = os.path.join(os.environ.get("HOME"), ".bash_history")
    contents = read_file_contents(history_file)
    lines = contents.split("\n")

    usage_map = {}

    for u_line in lines:
        line = u_line.strip()
        if line not in usage_map:
            usage_map[line] = 0

        usage_map[line] = usage_map[line] + 1

    usage_matrix = []
    for key in usage_map:
        usage_matrix.append([usage_map[key], key])

    usage_matrix = sorted(usage_matrix, cmp=sort_fun)

    for i in range(100):
        print(usage_matrix[i])
