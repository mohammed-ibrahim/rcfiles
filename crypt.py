import base64
import getpass
import sys
import os

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

def start(match_key):
    if len(sys.argv) != 3:
        print 'Usage: cry [-e|-d] <input>'
        sys.exit(0)

    x = sys.argv[1]
    if not x in ['-e', '-d']:
        print "Invalid command line option, use either -e or -d"
        sys.exit(0)

    input_content = sys.argv[2]
    pw = getpass.getpass()

    if pw == '' or pw == None:
        print "Invalid password."
        sys.exit(0)

    if pw != match_key:
        print "Password doesn't match."
        sys.exit(0)

    max_padding = 64
    if x == '-e':
        e1 = encode(pw, input_content)
        if len(e1) > max_padding:
            print 'Input password too long'
            sys.exit(0)

        e2 = encode(pw, e1.rjust(max_padding, ' '))
        print e2
    else:
        d1 = decode(pw, input_content)
        d2 = decode(pw, d1.strip())
        print d2

if __name__ == '__main__':
    encr_key = os.environ.get('ENCY_RTPS')
    if encr_key is None:
        print 'ENCY_RTPS env variable is not available.'
        sys.exit(0)
    start(base64.urlsafe_b64decode(encr_key))
