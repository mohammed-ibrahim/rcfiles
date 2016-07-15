import sys
import json
import traceback

def read_stdin():
    
    try:
        contents = json.loads(sys.stdin.read())
        return contents
    except Exception as e:
        print e.args
        return None


parsed = read_stdin()
print ''
if parsed is not None:
    print json.dumps(parsed, indent=4)
    print 'Json is Valid'
else:
    print 'Json is Invalid'
print ''
