import requests
import json
import os

def getUser():
    with open(os.path.dirname(__file__) + '/../../../credentials.json') as file:
        user = json.load(file)
    return user

def getToken(user):
    token_url = 'https://developers.onemap.sg/privateapi/auth/post/getToken'
    response = requests.post(url=token_url, json=user)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception('Failed to get token...')

def getLocation(latitude, longitude, token):
    # default (optional) params
    buffer = 10             # 0-500 > search radius
    addressType = 'All'     # HDB/All > show all HDB
    otherFeatures = 'N'     # Y/N > retrieve info on miscellaneous

    geocode_url = 'https://developers.onemap.sg/privateapi/commonsvc/revgeocode?location={},{}&token={}&buffer={}'
    response = requests.get(geocode_url.format(latitude, longitude, token, buffer))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to get location...')

if __name__ == '__main__':
    USER = getUser()
    TOKEN = getToken(USER)
    x, y = 1.38586107, 103.84561214
    x, y = 1.2896699905395508, 103.85006713867188
    LOCATION = getLocation(x, y, TOKEN)
    print(LOCATION)