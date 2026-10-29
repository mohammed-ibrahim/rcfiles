import os
import zipfile


def extract_fat_jar(jar_path: str, temp_dir: str) -> None:
    """
    Extract a fat jar into temp_dir, then extract every .jar found inside it
    into its own sub folder of temp_dir named after the child jar
    (e.g. BOOT-INF/lib/guava-33.0.jar -> temp_dir/guava-33.0/).
    """
    if not zipfile.is_zipfile(jar_path):
        raise ValueError(f"Not a valid jar/zip file: {jar_path}")

    os.makedirs(temp_dir, exist_ok=True)

    # 1. Extract the fat jar itself
    with zipfile.ZipFile(jar_path) as fat:
        fat.extractall(temp_dir)
        child_jars = [n for n in fat.namelist() if n.lower().endswith(".jar")]

    # 2. Extract each child jar into temp_dir/<child jar name>/
    used_names = set()
    for entry in child_jars:
        child_path = os.path.join(temp_dir, *entry.split("/"))
        base = os.path.splitext(os.path.basename(entry))[0]

        # Avoid clobbering when two child jars share a name in different dirs
        name, counter = base, 1
        while name in used_names:
            counter += 1
            name = f"{base}_{counter}"
        used_names.add(name)

        target = os.path.join(temp_dir, name)
        try:
            with zipfile.ZipFile(child_path) as child:
                child.extractall(target)
        except zipfile.BadZipFile:
            print(f"Skipping corrupt jar: {entry}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Usage: python extract_fat_jar.py <path-to-fat-jar> <temp-folder>")
        sys.exit(1)
    extract_fat_jar(sys.argv[1], sys.argv[2])