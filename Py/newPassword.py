import secrets
import string
import json

def newPassword():
    """Generates password of length 12"""
    
    num_chars = 12
    chars = string.ascii_letters + string.digits + ''.join([chr(i+ord('!')) for i in range(14)])
    password = ''.join(secrets.choice(chars) for _ in range(num_chars))

    print(f'Password: {password}')
    return password
    
if __name__ == '__main__':

    json_output = {
        'description': input('Enter description: '),
        'email': input('Enter email: '),
        'password': newPassword(),
    }

    with open('credentials.json', 'w') as file:
        json.dump(json_output, file, indent=4)

