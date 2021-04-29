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
    print(dir_prefix)
    key = Fernet.generate_key()

    try:
        with open(dir_prefix + '/.config/client_secret.json', 'rb') as file:
            data = file.read()
        encrypted_google = Fernet(key).encrypt(data)

        with open(dir_prefix + '/.config/api_key.json', 'rb') as file:
            data = file.read()
        encrypted_telegram = Fernet(key).encrypt(data)
        print('Encryption successful...')

        writeBytes(dir_prefix + '/.config/key.txt', key)
        writeBytes(dir_prefix + '/.config/secret_telegram.txt', encrypted_telegram)
        writeBytes(dir_prefix + '/.config/secret_google.txt', encrypted_google)

        # Set ENV
        with open(dir_prefix + '/.venv/bin/activate', 'a') as file:
            file.write(f'\nexport KEY="{key.decode()}"')
            print('KEY set successful')
            file.write(f'\nexport API_KEY="{encrypted_telegram.decode()}"')
            print('API_KEY set successful')
            file.write(f'\nexport CLIENT_SECRET="{encrypted_google.decode()}"')
            print('CLIENT_SECRET set successful')
            print('Reactivate venv to use new env...')
    except Exception as err:
        print(f'Encryption failed...\n{err}\nTry again...')

if __name__ == '__main__':
    start()