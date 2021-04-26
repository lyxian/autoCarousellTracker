import requests
import json

def getLocation(latitude, longitude):
    geocode_url = f'https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={latitude}&longitude={longitude}&localityLanguage=en'
    response = requests.get(geocode_url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to get location...')

if __name__ == '__main__':
    x, y = 1.38586107, 103.84561214
    x, y = 1.2896699905395508, 103.85006713867188
    LOCATION = getLocation(x, y)
    print(LOCATION)