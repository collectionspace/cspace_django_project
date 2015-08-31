from django.utils.crypto import get_random_string

def generate_secret_key(filename):
    newfile = open(filename, 'w')
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    newfile.write("SECRET_KEY = \"" + get_random_string(50, chars) + "\"")