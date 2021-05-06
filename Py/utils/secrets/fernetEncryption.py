# class-ify this
# convert dict to str > encode to bytes
# fernet.encrypt : bytes

from cryptography.fernet import Fernet
import json
import sys
import os

def writeBytes(filename, data):
    with open(filename, 'wb') as file:
        print(f'Saved to {filename}...')
        file.write(data)

def getEncryptionKey():
    try:
        dir_prefix = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        with open(dir_prefix + '/.config/key.txt', 'rb') as file:
            print('Reading existing key...')
            key = file.read()
        return key
    except:
        key = Fernet.generate_key()
        writeBytes(dir_prefix + '/.config/key.txt', key)
        return key

def start():
    dir_prefix = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    key = getEncryptionKey()

    try:
        # Encrypt secrets
        secrets = [filename for filename in os.listdir(dir_prefix + '/.config') if 'json' in filename]
        encrypted = {}
        for filename in secrets:
            name = filename.split('.')[0]
            with open(dir_prefix + f'/.config/{filename}', 'rb') as file:
                data = file.read()
            try:
                encrypted[name] = Fernet(key).encrypt(data)
                writeBytes(dir_prefix + f'/.config/secret_{name}.txt', encrypted[name])
                #print(f'Successful encryption of {filename}...')
            except:
                print(f'Encryption of {filename} failed...Try Again...')

        # Set ENV
        with open(dir_prefix + '/.venv/bin/activate', 'a') as file:
            file.write(f'\nexport KEY="{key.decode()}"')
            print('KEY set successful')
            for k, v in encrypted.items():
                file.write(f'\nexport {k.upper()}_KEY="{v.decode()}"')
                print(f'{k.upper()}_KEY set successful')
            print('Reactivate venv to use new env...')
    except Exception as err:
        print(f'Encryption failed...\n{err}\nTry again...')

if __name__ == '__main__':
    start()