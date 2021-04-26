import requests
import json
import sys
import os
sys.path.append(os.path.dirname(__file__) + '/../../../')

def getLocation(listing_id):
    listing_url = f'https://www.carousell.sg/api-service/listing/3.1/listings/{listing_id}/detail/'
    
    response = requests.get(listing_url)

    if response.status_code == 200:
        meta_values = response.json()['data']['screens'][0]['meta']['default_value']
        location_name = meta_values['location_name']
        if meta_values['meetup']:
            locations = [i['name'] for i in meta_values['meetups']]
        else:
            locations = None

        return location_name, locations
    else:
        raise Exception('Failed to get location...')

if __name__ == '__main__':
    query = 'google'; num = 10; exclude = ''

    from AutoCarousell_staging import searchCarousell, requestPayload, listingInfo

    base_url_filter = 'https://www.carousell.sg/api-service/filter/search/3.3/products/'
    response = searchCarousell(
        base_url_filter, requestPayload(query, num))
    
    for result in response['data']['results']:
        print(listingInfo(result['listingCard']))
        break
        listingCard = result['listingCard']
        print(getLocation(listingCard))