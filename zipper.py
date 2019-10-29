from zipfile import ZipFile, ZIP_DEFLATED
import os
import sys
import datetime
import time

def get_ts():
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%B-%d-%H-%M-%S')

def get_all_file_paths(directory):

	file_paths = []

	for root, directories, files in os.walk(directory):
		for filename in files:
			filepath = os.path.join(root, filename)
			file_paths.append(filepath)

	return file_paths

def make_zip(zip_file_name, directory):
	file_paths = get_all_file_paths(directory)

	print('Following files will be zipped:')
	for file_name in file_paths:
		print(file_name)

	with ZipFile(zip_file_name,'w') as zip:
		for file in file_paths:
			zip.write(file, os.path.basename(file), compress_type = ZIP_DEFLATED)

	print("Zipped to: %s" % zip_file_name)

def get_param(index):
    if len(sys.argv) > index:
        return sys.argv[index]

    return None

if __name__ == "__main__":
    zip_file_storage_directory = get_param(1)
    zip_source_files = get_param(2)

    if zip_file_storage_directory is None or zip_source_files is None:
        print("usage: zipper.py <zip-file-storage-dir> <direcotry-to-be-zipped>")
        sys.exit(1)

    file_name = "zipped-file-%s.zip" % (get_ts())
    zip_file_name = os.path.join(zip_file_storage_directory, file_name)
    print(zip_file_name)
    make_zip(zip_file_name, zip_source_files)
