import requests
import json
import re

def requiredHeaders():
    session = requests.Session()
    url = 'https://www.carousell.sg/'
    response = session.get(url)
    if response.ok:
        cookies = session.cookies.get_dict()
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'cookie': '_csrf={}'.format(cookies['_csrf']), # '; '.join([f'{i[0]}={i[1]}' for i in cookies.items()]),
        }
        response = session.get(url, headers=headers)
        if response.ok:
            appState = json.loads(re.search(r'.*Application":({[^}]*}).*', response.text).group(1))
        else:
            print('No cookies..')
            return ''
        headers['csrf-token'] = appState['csrfToken']
        return headers
    else:
        print('No cookies..')
        return ''