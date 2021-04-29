# class-ify this
# convert dict to str > encode to bytes
# fernet.encrypt : bytes

from cryptography.fernet import Fernet
import json
import sys
import os

def writeBytes(filename, data):
    with open(filename, 'wb') as file:
        print(f'Saved to {filename}')
        file.write(data)

def start():
    dir_prefix = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    key = Fernet.generate_key()

    try:
        with open(dir_prefix + '\\.config\\' + 'client_secret.json', 'rb') as file:
            data = file.read()
        fernet = Fernet(key)
        encrypted = fernet.encrypt(data)
        print('Encryption successful...')

        writeBytes(dir_prefix + '\\.config\\' + 'key.txt', key)
        writeBytes(dir_prefix + '\\.config\\' + 'secret.txt', encrypted)
    except:
        print('Encryption failed...\nTry again...')

if __name__ == '__main__':
    start()