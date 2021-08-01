import requests
import json

def requestPayload(query: str, num: int) -> dict:
    return {
        "count": num,
        "countryCode": "SG",
        "countryId": "1880251",
        "filters": [],
        "isFreeItems": False,
        "locale": "en",
        "prefill": {"prefill_sort_by": ""},
        "query": query
    }

def requestPayload_sorted(query: str, num: int) -> dict:
    return {
        "count": num,
        "countryCode": "SG",
        "countryId": "1880251",
        "filters": [],
        "isFreeItems": False,
        "locale": "en",
        "prefill": {"prefill_sort_by": "time_created,descending"},
        "query": query
    }

def searchCarousell(payload):
    base_url_filter = 'https://www.carousell.sg/api-service/filter/cf/4.0/search/'
    return requests.post(base_url_filter, json=payload).json()

if __name__ == '__main__':
    query = 'macbook'

    if 1:
        response = searchCarousell(requestPayload(query,40))
        results = response['data']['results']

        # Keep: title & date
        unsorted_json = [
            {
                'id': result['listingCard']['id'],
                'title': result['listingCard']['title'],
                'time': result['listingCard']['overlayContent']['timestampContent']['seconds']['low']
            } for result in results
        ]
        sorted_json = sorted(unsorted_json, key=lambda x: x['time'], reverse=True)

        with open('sorted.json', 'w') as file:
            json.dump(sorted_json, file)

        with open('unsorted.json', 'w') as file:
            json.dump(unsorted_json, file)
    if 1:
        response = searchCarousell(requestPayload_sorted(query,40))
        results = response['data']['results']

        # with open('result.json', 'w') as file:
        #     json.dump(results, file)

        sorted_1_json = [
            {
                'id': result['listingCard']['id'],
                'title': result['listingCard']['title'],
                'seller': result['listingCard']['seller']['username'],
                # 'time': result['listingCard']['overlayContent']['timestampContent']['seconds']['low']
            } for result in results
        ]

        with open('sorted_1.json', 'w') as file:
            json.dump(sorted_1_json, file)