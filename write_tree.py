import os


def write_tree(directory, max_depth):
    """
    Write the tree structure of `directory` to tree.txt inside the same
    directory, descending at most `max_depth` levels below it.

    max_depth=0 lists only the root, 1 includes its direct children, etc.
    Returns the path of the tree.txt file.
    """
    directory = os.path.abspath(directory)
    out_path = os.path.join(directory, "tree.txt")
    lines = [os.path.basename(directory) or directory]

    def walk(path, prefix, depth):
        if depth >= max_depth:
            return
        try:
            entries = sorted(
                os.listdir(path),
                key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower()),
            )
        except OSError as e:
            lines.append(f"{prefix}[error: {e.strerror}]")
            return

        # don't list the output file itself
        if depth == 0:
            entries = [e for e in entries if e != "tree.txt"]

        for i, name in enumerate(entries):
            full = os.path.join(path, name)
            last = i == len(entries) - 1
            lines.append(f"{prefix}{'└── ' if last else '├── '}{name}")
            # don't follow symlinked directories (avoids infinite loops)
            if os.path.isdir(full) and not os.path.islink(full):
                walk(full, prefix + ("    " if last else "│   "), depth + 1)

    walk(directory, "", 0)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return out_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python3 write_tree.py <directory> <max_depth>")
        sys.exit(1)

    print("Written:", write_tree(sys.argv[1], int(sys.argv[2])))