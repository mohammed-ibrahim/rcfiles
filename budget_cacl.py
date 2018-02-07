import sys

if len(sys.argv) != 2:
    print("usage: python python_file.py input_file.txt")
    sys.exit();


total = 0
with open(sys.argv[1]) as fp:  
    line = fp.readline()

    while line:
        parts = line.split(" ")
        if len(parts) > 0 and parts[0].isdigit():
            total = total + int(parts[0])
            print(line)

        line = fp.readline()

print 'total is: ' + str(total)
