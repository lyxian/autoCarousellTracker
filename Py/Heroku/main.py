### Heroku API ###

from cryptography.fernet import Fernet
import requests
import json
import os

def getApiKey(order):
    key = bytes(os.getenv('KEY'), 'utf-8')
    encrypted = bytes(os.getenv('HEROKU_KEY'), 'utf-8')
    return json.loads(Fernet(key).decrypt(encrypted))[f'api_key-{order}']

def requestHeaders(order):
    return {
        'Accept': 'application/vnd.heroku+json; version=3',
        'Authorization': f'Bearer {getApiKey(order)}',
        'Content-Type': 'application/json',
    }

def chooseApp():
    url = 'https://api.heroku.com/apps'
    response = requests.get(url=url, headers=requestHeaders())
    appNames = [app['name'] for app in response.json()]
    app = ''
    while app not in appNames:
        print('List of apps:', end=' ')
        print(*appNames, sep=', ')
        app = input('Choose app: ')
    return app

class App():

    class Formation():
        def __init__(self, response):
            self.id = response['id']
            self.type = response['type']
            self.size = response['size']
            self.quantity = response['quantity']

    def formationInfo(self):
        "List formations in app"
        url = self.url.format(f'apps/{self.name}/formation')
        response = requests.get(url=url, headers=self.headers) #, json=data)
        if response.ok:
            self.formations = [self.Formation(i) for i in response.json()]
            # print('List of dynos:', end=' ')
            # print(*[formation.id for formation in self.formations], sep=', ')
        else:
            print('Request returns', response.status_code, '\n')
            try:
                print(response.json())
            except:
                print(response.content)

    def __init__(self, name, order):
        self.name = name
        self.url = 'https://api.heroku.com/{}'
        self.headers = requestHeaders(order)
        self.formationInfo()

    def enable(self, x: bool):
        "Enable/Disable Heroku App via API-Formation"
        action = 'enable' if x else 'disable'
        for formation in self.formations:
            url = self.url.format(f'apps/{self.name}/formation')
            updates = {
                'updates': [{
                    'quantity': int(x),
                    'type': formation.type,
                    'size': formation.size,
                }]
            }
            response = requests.patch(url=url, headers=self.headers, json=updates)
            if response.ok:
                print(f'Successfully {action} {formation.id}...')
            else:
                print(f'Fail to {action} {formation.id}...\nRequest returns {response.status_code}')
                print(response.json())

if __name__ == '__main__':
    # app = App(chooseApp())
    app = App('yxian--test', 1)
    app.enable(True)