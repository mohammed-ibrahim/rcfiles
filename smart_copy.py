import os
import pyperclip
import sys

program_name = sys.argv[0]


def copy_to_clip(pbuf):
    joined = " ".join(pbuf)
    #os.system("echo '%s' | pbcopy" % joined)
    pyperclip.copy(joined)

buf = list()

if len(sys.argv) == 1:
    for line in sys.stdin:
        buf.append(line[:-1])

    print("Copying: " + str(buf))
    copy_to_clip(buf)
    sys.exit(0)


if len(sys.argv) == 2:
    num = int(sys.argv[1])

    for line in sys.stdin:
        buf.append(line[:-1])

    print("Copying: " + buf[num])
    tbuf = [buf[num]]
    copy_to_clip(tbuf)

    sys.exit(0)


print("Invalid usage of smart_copy")
sys.exit(1)

