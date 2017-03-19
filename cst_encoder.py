import sys
import os
import base64
import random
import getpass

"""
CstEncoder encoder class
"""
class CstEncoder:
    def get_str_list(self, text):
        la = list()
        for ia in text:
            la.append(ia)
    
        return la
    
    def encode(self, vector, password, text_to_encode):
        vector = self.get_str_list(vector)
        password = self.get_str_list(password)
    
        encoded_string = ""
        password_index = 0
        for text_char in text_to_encode:
            next_random_character = random.choice(vector)
    
            while next_random_character != password[password_index]:
                encoded_string += next_random_character
                next_random_character = random.choice(vector)
    
            encoded_string += next_random_character
            encoded_string += text_char
            password_index += 1
    
            if password_index > len(password) - 1:
                password_index = 0
    
        return encoded_string
    
    def decode(self, password, text_to_decode):
        password = self.get_str_list(password)
    
        decoded_string = ""
        password_index = 0
        payload_length = len(text_to_decode)
        item_index = 0
    
        while item_index < len(text_to_decode)-1:
            if text_to_decode[item_index] == password[password_index]:
                decoded_string += text_to_decode[item_index+1]
                password_index += 1
                item_index += 1
    
                if password_index > len(password) - 1:
                    password_index = 0
    
            item_index += 1
    
        return decoded_string

"""
String ops class
"""
class StringOps:
    vector = 'abcdefghijklmnopqrstuvwxyz01234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ!@#$%^&*()?._'

    def get_vector(self):
        return self.vector
    
    def get_password(self):
        encr_key = os.environ.get('ENCY_RTPS')
        if encr_key is None:
            print 'ENCY_RTPS env variable is not available.'
            sys.exit(0)

        unsafe_cased_key = base64.urlsafe_b64decode(encr_key)
        return unsafe_cased_key.lower()
        #return getpass.getpass()
    
    def get_prod_vector_and_password(self):
        vector = self.get_vector()
        password = self.get_password()
    
        for password_char in password:
            if not password_char in vector:
                print "Invalid password: Password contains characters that are not supported."
                sys.exit(0)
    
        return (vector, password)
    
    def get_random_string(self):
        passlen = random.randint(1,len(self.vector))
        randomly_generated_password = "".join(random.sample(self.vector,passlen))
        return randomly_generated_password


def test():
    print 'Testing...'

    string_ops = StringOps()
    cst_encoder = CstEncoder()

    for i in range(1000):
        input_string = string_ops.get_random_string()
        password = string_ops.get_random_string()
        vector = string_ops.get_vector()

        encoded = cst_encoder.encode(vector, password, input_string)
        decoded = cst_encoder.decode(password, encoded)

        if input_string != decoded:
            print "Failed"
            sys.exit(0)

    print "Passed"

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print 'program [-e|-d] <input>'
        sys.exit(0)

    option = sys.argv[1]
    if not option in ['-e', '-d', '-t']:
        print 'Invalid option.'
        print 'program [-e|-d] <input>'
        sys.exit(0)

    if option == '-t':
        test()
        sys.exit(0);

    string_ops = StringOps()
    (vector, password) = string_ops.get_prod_vector_and_password()

    cst_encoder = CstEncoder()

    if option == '-e':
        print cst_encoder.encode(vector, password, sys.argv[2])
    else:
        print cst_encoder.decode(password, sys.argv[2])
