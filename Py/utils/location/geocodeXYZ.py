import requests
import json

def getLocation(latitude, longitude):
    geocode_url = 'https://geocode.xyz/{},{}?json=1'
    response = requests.get(geocode_url.format(latitude, longitude))

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to get location...')

if __name__ == '__main__':
    x, y = 1.38586107, 103.84561214
    LOCATION = getLocation(x, y)
    print(LOCATION)