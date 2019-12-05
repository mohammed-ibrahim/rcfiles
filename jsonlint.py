import sys
import json
import traceback
from collections import OrderedDict

def read_stdin(ordered_keys):

    try:
        if ordered_keys:
            contents = json.loads(sys.stdin.read(), object_pairs_hook=OrderedDict)
            return contents

        else:
            contents = json.loads(sys.stdin.read())
            return contents

    except Exception as e:
        print( e.args)
        return None

ordered_keys = False
if len(sys.argv) == 2 and sys.argv[1] == '-o':
    ordered_keys = True


parsed = read_stdin(ordered_keys)

print( '')
if parsed is not None:
    print (json.dumps(parsed, indent=4))
else:
    print ('Json is Invalid')
print ('')
