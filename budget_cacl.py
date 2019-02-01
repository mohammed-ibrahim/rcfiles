import sys

if len(sys.argv) != 2:
    print("usage: python python_file.py input_file.txt")
    sys.exit();


total = 0
with open(sys.argv[1]) as fp:  
    line = fp.readline()
    content = []

    while line:
        parts = line.split(" ")
        if len(parts) > 0 and parts[0].isdigit():
            amount = int(parts[0])
            total = total + amount
            print(line)
            content.append("%07d %s" % (amount, line.replace("\n", "")))

        line = fp.readline()
content.sort()
print("\n".join(content))
print 'total is: ' + str(total)
