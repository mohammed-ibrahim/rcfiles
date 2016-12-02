import base64
import getpass
import sys

def encode(password, input_to_encode):
    encoded_object = []
    for i in range(len(input_to_encode)):
        key_c = password[i % len(password)]
        enc_c = chr((ord(input_to_encode[i]) + ord(key_c)) % 256)
        encoded_object.append(enc_c)
    return base64.urlsafe_b64encode("".join(encoded_object))

def decode(password, encoded_object):
    dec = []
    encoded_object = base64.urlsafe_b64decode(encoded_object)
    for i in range(len(encoded_object)):
        key_c = password[i % len(password)]
        dec_c = chr((256 + ord(encoded_object[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)

x = raw_input('(e)ncode or (d)ecode? : ')
if not x in ['e', 'd']:
    print "Invalid input."
    sys.exit(0)

input_content = raw_input('Enter Input: ')
pw = getpass.getpass()

if pw == '' or pw == None:
    print "Invalid password."
    sys.exit(0)

if x == 'e':
    print(encode(pw, input_content))
else:
    print(decode(pw, input_content))
