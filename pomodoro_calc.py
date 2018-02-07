import sys

if len(sys.argv) != 2:
    print("usage: python python_file.py input_file.txt")
    sys.exit();


total_pomodoros = 0
failed = 0
num_days = 0
num_days_worked = 0
with open(sys.argv[1]) as fp:  
    line = fp.readline()

    while line:
        line = line.replace("\n", "")
        parts = line.split(" ")
        last_item_index = len(parts) - 1
        if len(parts) > 0:
            num_days = num_days + 1
            print(line)
            print(parts)

            if parts[last_item_index].isdigit():
                total_pomodoros = total_pomodoros + int(parts[last_item_index])
                num_days_worked = num_days_worked + 1
                print("passed")
            if parts[last_item_index].lower() == 'f':
                failed = failed + 1
                print("failed")

        line = fp.readline()

print("Total pomodoros: %d Days Worked: %d Days Failed: %d Work Percentage: %f" % (total_pomodoros, num_days_worked, failed, (float(num_days_worked)/float(num_days_worked+failed))))
